"""Compilador de Brainfuck → SpellCode.

Demuestra que SpellCode es Turing-completo: cualquier programa
Brainfuck puede traducirse a SpellCode preservando la semántica.

Mapeo exacto:
  >  →  Depulso
  <  →  Levioso
  +  →  Lumos
  -  →  Nox
  .  →  Sonorus
  ,  →  Accio
  [  →  Protego
  ]  →  Finite

Todo carácter que no sea un operador Brainfuck se ignora
(igual que en Brainfuck estándar: comentarios implícitos).
"""
from __future__ import annotations

_BF_MAP: dict[str, str] = {
    ">": "Depulso",
    "<": "Levioso",
    "+": "Lumos",
    "-": "Nox",
    ".": "Sonorus",
    ",": "Accio",
    "[": "Protego",
    "]": "Finite",
}


def bf_to_spellcode(bf_source: str) -> str:
    """Traduce código Brainfuck a código SpellCode (un hechizo por línea)."""
    lines: list[str] = []
    for ch in bf_source:
        spell = _BF_MAP.get(ch)
        if spell is not None:
            lines.append(spell)
    return "\n".join(lines) + "\n"
