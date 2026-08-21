"""SpellCode — esolang experimental basado en hechizos.

API pública:
  - parse(source)         → (tokens, jump_table)
  - run(source, input=...) → bytes de salida
  - VM                    — máquina virtual explícita
"""
from __future__ import annotations

from .parser import parse, parse_full, tokenize, precompute_jumps, SpellCodeParseError
from .vm import VM, SpellCodeError

__version__ = "0.1.0"

__all__ = [
    "parse", "parse_full", "tokenize", "precompute_jumps", "SpellCodeParseError",
    "VM", "SpellCodeError", "run",
]


def run(source: str, input_data: bytes = b"") -> bytes:
    """Compila+ejecuta un programa SpellCode. Devuelve la salida."""
    tokens, jumps, breaks = parse_full(source)
    vm = VM()
    vm.reset(tokens, jumps, input_data, breaks)
    return vm.run()
