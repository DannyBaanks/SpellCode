"""Tests del compilador Brainfuck → SpellCode (TESTURINGS)."""
from __future__ import annotations

import unittest

from spellcode.bf_compiler import bf_to_spellcode
from spellcode import run


class BFCompilerTests(unittest.TestCase):
    def test_mapping_completeness(self):
        sc = bf_to_spellcode("><+-.,[]")
        # Cada operador BF produce su hechizo
        from spellcode.parser import tokenize
        tokens = tokenize(sc)
        self.assertEqual(tokens, [
            "Depulso", "Levioso", "Lumos", "Nox",
            "Sonorus", "Accio", "Protego", "Finite",
        ])

    def test_non_bf_chars_ignored(self):
        sc = bf_to_spellcode("+ comment\n- . ")
        from spellcode.parser import tokenize
        tokens = tokenize(sc)
        self.assertEqual(tokens, ["Lumos", "Nox", "Sonorus"])

    def test_hello_world(self):
        # Hello World en Brainfuck
        bf = (
            "++++++++[>++++++++<-]>+++++++++++++++.----.--.+++.---."
            "------------.+++++.--------.+++.------.--------.-"
        )
        # Ajustar: usar el hello world estándar
        bf_hello = (
            "++++++++++[>+++++++>++++++++++>+++>+<<<<-]"
            ">++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++."
            "------.--------.>+.>."
        )
        sc = bf_to_spellcode(bf_hello)
        out = run(sc)
        self.assertEqual(out, b"Hello World!\n")

    def test_cat_program(self):
        # cat: ,[.,]
        bf = ",[.,]"
        sc = bf_to_spellcode(bf)
        out = run(sc, b"Hola")
        self.assertEqual(out, b"Hola")

    def test_add_two_numbers(self):
        # Lee 2 bytes, suma, imprime: ,>,[<+>-]<.
        bf = ",>,[<+>-]<."
        sc = bf_to_spellcode(bf)
        # 1 + 1 = 2 (carácter \x02)
        out = run(sc, b"\x01\x01")
        self.assertEqual(out, b"\x02")


if __name__ == "__main__":
    unittest.main()
