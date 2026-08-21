"""Tests de la tabla de hechizos — resolución, alias, familias."""
from __future__ import annotations

import unittest

from spellcode.spells import (
    SPELL_TABLE, SPELL_REGISTRY, FAMILIES,
    CORE_SPELLS, resolve, OPCODE_TO_SPELL,
)


class SpellTableTests(unittest.TestCase):
    def test_core_has_8_spells(self):
        self.assertEqual(len(CORE_SPELLS), 8)

    def test_all_core_in_table(self):
        for name in CORE_SPELLS:
            self.assertIn(name, SPELL_TABLE)

    def test_resolve_canonical(self):
        self.assertEqual(resolve("Lumos"), "Lumos")

    def test_resolve_alias_space(self):
        self.assertEqual(resolve("Avada Kedavra"), "AvadaKedavra")

    def test_resolve_finite_incantatem(self):
        self.assertEqual(resolve("Finite Incantatem"), "Finite")

    def test_resolve_unknown_returns_none(self):
        self.assertIsNone(resolve("Patronus"))

    def test_registry_has_info_for_every_spell(self):
        for name in SPELL_TABLE:
            self.assertIn(name, SPELL_REGISTRY)

    def test_families_cover_all_spells(self):
        all_in_families = set()
        for members in FAMILIES.values():
            all_in_families.update(members)
        self.assertEqual(all_in_families, set(SPELL_TABLE.keys()))

    def test_opcode_to_spell_injective(self):
        self.assertEqual(len(OPCODE_TO_SPELL), len(SPELL_TABLE))


if __name__ == "__main__":
    unittest.main()
