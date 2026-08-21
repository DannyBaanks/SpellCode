"""CLI de SpellCode.

Uso:
  spellcode programa.spell              # ejecuta leyendo stdin
  spellcode programa.spell -i entrada   # ejecuta con input de archivo
  spellcode -c "Lumos Sonorus Nox"      # ejecuta desde string
  spellcode --dump programa.spell       # muestra tokens + saltos
  spellcode --from-bf programa.bf       # compila Brainfuck a SpellCode
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import parse, run
from .vm import SpellCodeError
from .parser import SpellCodeParseError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="spellcode",
        description="Intérprete del esolang SpellCode.",
    )
    parser.add_argument("file", nargs="?", help="archivo .spell")
    parser.add_argument("-c", "--code", help="ejecutar código inline")
    parser.add_argument("-i", "--input", type=Path,
                        help="archivo de entrada (bytes)")
    parser.add_argument("-n", "--input-text", help="texto de entrada")
    parser.add_argument("--dump", action="store_true",
                        help="mostrar tokens y tabla de saltos")
    parser.add_argument("--from-bf", dest="from_bf", action="store_true",
                        help="interpretar el archivo como Brainfuck y traducir a SpellCode")
    args = parser.parse_args(argv)

    # Resolver fuente
    if args.code:
        source = args.code
    elif args.file:
        source = Path(args.file).read_text(encoding="utf-8")
    else:
        parser.print_help()
        return 1

    # Resolver entrada
    input_data = b""
    if args.input:
        input_data = args.input.read_bytes()
    elif args.input_text is not None:
        input_data = args.input_text.encode("utf-8")

    # Traducir Brainfuck si se solicitó
    if args.from_bf:
        from .bf_compiler import bf_to_spellcode
        source = bf_to_spellcode(source)

    # Compilar
    try:
        tokens, jumps = parse(source)
    except SpellCodeParseError as exc:
        print(f"spellcode: error de sintaxis: {exc}", file=sys.stderr)
        return 2

    if args.dump:
        from .spells import SPELL_TABLE
        print(f"Tokens ({len(tokens)}):")
        for i, tok in enumerate(tokens):
            op = SPELL_TABLE.get(tok, "?")
            jmp = jumps[i]
            print(f"  [{i:4d}] {tok:20s}  op={op:12s}  jump={jmp}")
        return 0

    # Ejecutar
    from .vm import VM
    vm = VM()
    vm.reset(tokens, jumps, input_data)
    try:
        output = vm.run()
    except SpellCodeError as exc:
        print(f"spellcode: error de ejecución: {exc}", file=sys.stderr)
        return 3

    # Escribir salida a stdout (raw bytes)
    sys.stdout.buffer.write(output)
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
