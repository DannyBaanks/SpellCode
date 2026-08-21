"""Tests de la VM — hechizos individuales y comportamiento."""
from __future__ import annotations

import unittest

from spellcode.parser import parse, parse_full
from spellcode.vm import VM, SpellCodeError


def exec_src(src: str, input_data: bytes = b"") -> bytes:
    tokens, jumps, breaks = parse_full(src)
    vm = VM()
    vm.reset(tokens, jumps, input_data, breaks)
    return vm.run()


def reset_vm(src: str, input_data: bytes = b"") -> VM:
    tokens, jumps, breaks = parse_full(src)
    vm = VM()
    vm.reset(tokens, jumps, input_data, breaks)
    return vm


class CoreSpellTests(unittest.TestCase):
    def test_lumos_increments(self):
        vm = reset_vm("Lumos Lumos Lumos")
        vm.run()
        self.assertEqual(vm.tape[0], 3)

    def test_nox_decrements(self):
        vm = reset_vm("Lumos Lumos Lumos Lumos Nox Nox")
        vm.run()
        self.assertEqual(vm.tape[0], 2)

    def test_wraparound_overflow(self):
        vm = reset_vm("Nox")
        vm.run()
        self.assertEqual(vm.tape[0], 255)

    def test_wraparound_underflow(self):
        vm = reset_vm("Lumos " * 256)
        vm.run()
        self.assertEqual(vm.tape[0], 0)

    def test_depulso_moves_right(self):
        vm = reset_vm("Lumos Depulso Lumos")
        vm.run()
        self.assertEqual(vm.tape[0], 1)
        self.assertEqual(vm.tape[1], 1)
        self.assertEqual(vm.head, 1)

    def test_levioso_moves_left(self):
        vm = reset_vm("Depulso Depulso Lumos Levioso Lumos")
        vm.run()
        self.assertEqual(vm.tape[2], 1)
        self.assertEqual(vm.tape[1], 1)
        self.assertEqual(vm.head, 1)

    def test_levioso_at_zero_raises(self):
        with self.assertRaises(SpellCodeError):
            exec_src("Levioso")

    def test_sonorus_outputs_byte(self):
        out = exec_src("Lumos " * 65 + "Sonorus")
        self.assertEqual(out, b"A")

    def test_accio_reads_input(self):
        out = exec_src("Accio Sonorus", b"Z")
        self.assertEqual(out, b"Z")

    def test_accio_empty_input_returns_zero(self):
        out = exec_src("Accio Sonorus", b"")
        self.assertEqual(out, b"\x00")


class LoopTests(unittest.TestCase):
    def test_simple_loop(self):
        # [>+<-] — copia celda 0 a celda 1 (vía resta/suma)
        src = "Lumos Lumos Lumos Protego Depulso Lumos Levioso Nox Finite"
        vm = reset_vm(src)
        vm.run()
        self.assertEqual(vm.tape[0], 0)
        self.assertEqual(vm.tape[1], 3)

    def test_loop_skipped_if_zero(self):
        src = "Protego Lumos Finite Sonorus"
        out = exec_src(src)
        self.assertEqual(out, b"\x00")

    def test_nested_loops_parse_and_run(self):
        vm = reset_vm("Protego Protego Lumos Finite Finite")
        vm.run()
        self.assertTrue(True)


class StackSpellTests(unittest.TestCase):
    def test_aguamenti_pushes(self):
        vm = reset_vm("Lumos Lumos Aguamenti")
        vm.run()
        self.assertEqual(vm.stack, [2])

    def test_incendio_pops_and_adds(self):
        vm = reset_vm("Lumos Lumos Aguamenti Lumos Incendio")
        vm.run()
        self.assertEqual(vm.tape[0], 5)
        self.assertEqual(vm.stack, [])

    def test_evanesco_discards(self):
        vm = reset_vm("Lumos Aguamenti Evanesco")
        vm.run()
        self.assertEqual(vm.stack, [])

    def test_gemino_duplicates(self):
        vm = reset_vm("Lumos Lumos Aguamenti Gemino")
        vm.run()
        self.assertEqual(vm.stack, [2, 2])

    def test_expelliarmus_pops_and_subs(self):
        vm = reset_vm("Lumos Lumos Lumos Aguamenti Expelliarmus")
        vm.run()
        self.assertEqual(vm.tape[0], 0)

    def test_incendio_empty_stack_raises(self):
        with self.assertRaises(SpellCodeError):
            exec_src("Incendio")

    def test_evanesco_empty_stack_raises(self):
        with self.assertRaises(SpellCodeError):
            exec_src("Evanesco")

    def test_gemino_empty_stack_raises(self):
        with self.assertRaises(SpellCodeError):
            exec_src("Gemino")


class StateSpellTests(unittest.TestCase):
    def test_reparo_zeros_cell(self):
        vm = reset_vm("Lumos Lumos Reparo")
        vm.run()
        self.assertEqual(vm.tape[0], 0)

    def test_muffliato_noop(self):
        vm = reset_vm("Lumos Muffliato Lumos")
        vm.run()
        self.assertEqual(vm.tape[0], 2)

    def test_avada_kedavra_halts(self):
        vm = reset_vm("Lumos AvadaKedavra Lumos")
        vm.run()
        self.assertEqual(vm.tape[0], 1)
        self.assertTrue(vm.halted)

    def test_stupefy_outside_loop_raises(self):
        with self.assertRaises(SpellCodeError):
            exec_src("Stupefy")

    def test_stupefy_breaks_loop(self):
        # Lumos (cell0=1) → Protego entra → Lumos (cell0=2) → Stupefy sale
        vm = reset_vm("Lumos Protego Lumos Stupefy Finite Sonorus")
        vm.run()
        self.assertEqual(vm.tape[0], 2)
        self.assertEqual(bytes(vm.output), b"\x02")


if __name__ == "__main__":
    unittest.main()
