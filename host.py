#!/usr/bin/env python3
"""
SpellCode Host — motor público genérico, todo en uno.

Wrapper fino del CLI de SpellCode para uso público.
No expone infraestructura interna, solo el parser y la VM.

Uso:
  py host.py programa.spell
  py host.py --list
  py host.py --all
  py host.py -c "Lumos Sonorus"
"""

from __future__ import annotations

import sys
from pathlib import Path

# Reusa el motor público
from spellcode.parser import parse_full
from spellcode.vm import VM
from spellcode.spells import SPELL_REGISTRY

def list_spells() -> None:
    print("SpellCode — 17 hechizos (8 núcleo + 9 extensión)")
    print("=" * 60)
    for name, info in sorted(SPELL_REGISTRY.items(), key=lambda x: x[0].lower()):
        print(f"{name:18s} {info.family:14s} # {info.behavior}")
    print(f"\nTotal: {len(SPELL_REGISTRY)}")
    core = [k for k,v in SPELL_REGISTRY.items() if k in ["Lumos","Nox","Depulso","Levioso","Protego","Finite","Accio","Sonorus"]]
    print(f"Núcleo TC: {', '.join(sorted(core))}")

def run_file(path: Path, input_data: bytes = b"") -> int:
    source = path.read_text(encoding="utf-8")
    try:
        tokens, jumps, breaks = parse_full(source)
    except Exception as e:
        print(f"Error de sintaxis {path.name}: {e}", file=sys.stderr)
        return 2
    vm = VM()
    vm.reset(tokens, jumps, input_data, breaks)
    try:
        out = vm.run()
        if out:
            sys.stdout.buffer.write(out)
            sys.stdout.buffer.write(b"\n")
        return 0
    except Exception as e:
        print(f"Error de ejecución {path.name}: {e}", file=sys.stderr)
        return 3

def main() -> None:
    import argparse
    p = argparse.ArgumentParser(description="SpellCode Host — ejecuta .spell")
    p.add_argument("file", nargs="?", help="Archivo .spell")
    p.add_argument("-c", "--code", help="Código inline")
    p.add_argument("--list", action="store_true", help="Lista 17 hechizos")
    p.add_argument("--all", action="store_true", help="Ejecuta todo el corpus")
    p.add_argument("--dump", action="store_true", help="Muestra tokens y saltos")
    args = p.parse_args()

    if args.list:
        list_spells()
        return

    if args.all:
        corpus = sorted((Path(__file__).parent / "corpus").glob("*.spell"))
        if not corpus:
            print("corpus vacío, ejecuta gen_17_spell.py", file=sys.stderr)
            sys.exit(2)
        fails = 0
        for f in corpus:
            code = run_file(f)
            print(f"{f.name}: {'OK' if code==0 else 'FAIL'}")
            if code != 0:
                fails += 1
        print(f"\nCorpus: {len(corpus)-fails}/{len(corpus)} OK")
        sys.exit(1 if fails else 0)

    if args.code:
        from spellcode.parser import parse_full
        from spellcode.vm import VM
        tokens, jumps, breaks = parse_full(args.code)
        vm = VM()
        vm.reset(tokens, jumps, b"", breaks)
        out = vm.run()
        sys.stdout.buffer.write(out)
        return

    if args.file:
        sys.exit(run_file(Path(args.file)))

    p.print_help()

if __name__ == "__main__":
    main()
