"""Tests del parser: tokenización, alias, comentarios, errores."""
from __future__ import annotations

import unittest

from spellcode.parser import SpellCodeParseError, parse, tokenize


class TokenizeTests(unittest.TestCase):
    def test_single_spell(self):
        self.assertEqual(tokenize("Lumos"), ["Lumos"])

    def test_multiple_spells_on_one_line(self):
        self.assertEqual(tokenize("Lumos Sonorus"), ["Lumos", "Sonorus"])

    def test_multiple_lines(self):
        src = "Lumos\nNox\nSonorus\n"
        self.assertEqual(tokenize(src), ["Lumos", "Nox", "Sonorus"])

    def test_spells_and_spaces(self):
        src = "Lumos  Nox   Sonorus"
        self.assertEqual(tokenize(src), ["Lumos", "Nox", "Sonorus"])

    def test_comment_is_ignored(self):
        src = "Lumos # esto es un comentario\nNox"
        self.assertEqual(tokenize(src), ["Lumos", "Nox"])

    def test_full_line_comment(self):
        src = "# comentario completo\nLumos"
        self.assertEqual(tokenize(src), ["Lumos"])

    def test_blank_lines_ignored(self):
        src = "\n\nLumos\n\n\nNox\n\n"
        self.assertEqual(tokenize(src), ["Lumos", "Nox"])

    def test_alias_avada_kedavra_with_space(self):
        src = "Avada Kedavra"
        self.assertEqual(tokenize(src), ["AvadaKedavra"])

    def test_alias_finite_incantatem(self):
        src = "Finite Incantatem"
        self.assertEqual(tokenize(src), ["Finite"])

    def test_mixed_case_raises(self):
        with self.assertRaises(SpellCodeParseError):
            tokenize("lumos")

    def test_unknown_spell_raises(self):
        with self.assertRaises(SpellCodeParseError):
            tokenize("Patronus")

    def test_empty_source(self):
        self.assertEqual(tokenize(""), [])


class JumpTableTests(unittest.TestCase):
    def test_balanced_loops(self):
        src = "Protego Lumos Finite"
        tokens, jumps = parse(src)
        self.assertEqual(jumps[0], 2)
        self.assertEqual(jumps[2], 0)

    def test_nested_loops(self):
        src = "Protego Protego Lumos Finite Finite"
        tokens, jumps = parse(src)
        self.assertEqual(jumps[0], 4)
        self.assertEqual(jumps[1], 3)
        self.assertEqual(jumps[3], 1)
        self.assertEqual(jumps[4], 0)

    def test_unbalanced_open_raises(self):
        with self.assertRaises(SpellCodeParseError):
            parse("Protego Lumos")

    def test_unbalanced_close_raises(self):
        with self.assertRaises(SpellCodeParseError):
            parse("Lumos Finite")

    def test_no_loops_all_minus_one(self):
        tokens, jumps = parse("Lumos Nox Sonorus")
        self.assertEqual(jumps, [-1, -1, -1])


if __name__ == "__main__":
    unittest.main()
