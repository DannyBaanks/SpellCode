#!/usr/bin/env python3
"""
Genera 17 .spell canónicos — uno por hechizo — verificados con la VM.
Cada archivo es flashcard ejecutable mínima, no sustituye tests/.
"""

import sys
from pathlib import Path

from spellcode.vm import VM
from spellcode.parser import parse_full

OUT = Path("corpus")
OUT.mkdir(exist_ok=True)

# 17 hechizos — forma mínima válida por spell
CORPUS = {
    "001_Lumos.spell": """# 001 Lumos — inc cell[head] +=1
# PRE: cell=0
# POST: cell=1
Lumos
AvadaKedavra
""",
    "002_Nox.spell": """# 002 Nox — dec cell[head] -=1 (mod 256)
# PRE: cell=1
# POST: cell=0
Lumos
Nox
AvadaKedavra
""",
    "003_Depulso.spell": """# 003 Depulso — head +=1
# PRE: head=0
# POST: head=1, cell[1]=0
Depulso
AvadaKedavra
""",
    "004_Levioso.spell": """# 004 Levioso — head -=1
# PRE: head=1
# POST: head=0
Depulso
Levioso
AvadaKedavra
""",
    "005_Protego.spell": """# 005 Protego — loop start (if cell==0 jump Finite)
# PRE: cell=0
# POST: salta bloque, cell=0
Protego
Lumos
Finite
AvadaKedavra
""",
    "006_Finite.spell": """# 006 Finite — loop end (if cell!=0 jump Protego)
# PRE: cell=1, loop 1 vez
# POST: cell=0 tras 1 iter
Lumos
Protego
Nox
Finite
AvadaKedavra
""",
    "007_Accio.spell": """# 007 Accio — cell = input byte (0 si no hay)
# PRE: input=[65]
# POST: cell=65 ('A')
Accio
AvadaKedavra
""",
    "008_Sonorus.spell": """# 008 Sonorus — output cell
# PRE: cell=1
# POST: output b'\\x01'
Lumos
Sonorus
AvadaKedavra
""",
    "009_Aguamenti.spell": """# 009 Aguamenti — push cell to stack
# PRE: cell=3, stack=[]
# POST: stack=[3]
Lumos
Lumos
Lumos
Aguamenti
AvadaKedavra
""",
    "010_Incendio.spell": """# 010 Incendio — pop stack + add to cell
# PRE: cell=2, stack=[3]
# POST: cell=5
Lumos
Lumos
Aguamenti
Lumos
Incendio
AvadaKedavra
""",
    "011_Evanesco.spell": """# 011 Evanesco — pop stack + discard
# PRE: stack=[5]
# POST: stack=[]
Lumos
Lumos
Lumos
Aguamenti
Evanesco
AvadaKedavra
""",
    "012_Gemino.spell": """# 012 Gemino — duplicate stack top
# PRE: stack=[4]
# POST: stack=[4,4]
Lumos
Lumos
Lumos
Lumos
Aguamenti
Gemino
AvadaKedavra
""",
    "013_Expelliarmus.spell": """# 013 Expelliarmus — pop stack + sub from cell
# PRE: cell=13, stack=[10]
# POST: cell=3 (13-10), stack=[]
Lumos
Lumos
Lumos
Lumos
Lumos
Lumos
Lumos
Lumos
Lumos
Lumos
Aguamenti
Lumos
Lumos
Lumos
Expelliarmus
AvadaKedavra
""",
    "014_Reparo.spell": """# 014 Reparo — cell = 0
# PRE: cell=5
# POST: cell=0
Lumos
Lumos
Lumos
Lumos
Lumos
Reparo
AvadaKedavra
""",
    "015_Muffliato.spell": """# 015 Muffliato — NOP
# PRE: -
# POST: -
Muffliato
AvadaKedavra
""",
    "016_Stupefy.spell": """# 016 Stupefy — break innermost loop
# PRE: cell=5, loop 5 veces, break en 1ª
# POST: cell=5, sale del loop sin completar Nox
Lumos
Lumos
Lumos
Lumos
Lumos
Protego
Stupefy
Nox
Finite
AvadaKedavra
""",
    "017_AvadaKedavra.spell": """# 017 AvadaKedavra — halt
# PRE: -
# POST: halt inmediato
AvadaKedavra
""",
}

def _check_post(fname: str, vm: VM):
    """Verifica POST del corpus contra estado real (no solo 'no lanzó')."""
    # Checks basados en los comentarios PRE/POST de cada flashcard
    if fname == "001_Lumos.spell":
        assert vm.tape[0] == 1, f"Lumos POST cell=1, got {vm.tape[0]}"
    elif fname == "002_Nox.spell":
        assert vm.tape[0] == 0, f"Nox POST cell=0, got {vm.tape[0]}"
    elif fname == "003_Depulso.spell":
        assert vm.head == 1, f"Depulso POST head=1, got {vm.head}"
    elif fname == "004_Levioso.spell":
        assert vm.head == 0, f"Levioso POST head=0, got {vm.head}"
    elif fname == "005_Protego.spell":
        assert vm.tape[0] == 0, "Protego debe saltar bloque"
    elif fname == "006_Finite.spell":
        assert vm.tape[0] == 0, "Finite POST cell=0 tras 1 iter"
    elif fname == "007_Accio.spell":
        assert vm.tape[0] == 65, f"Accio POST cell=65, got {vm.tape[0]}"
    elif fname == "008_Sonorus.spell":
        assert vm.output == b"\x01", f"Sonorus output b'\\x01', got {vm.output!r}"
    elif fname == "009_Aguamenti.spell":
        assert vm.stack == [3], f"Aguamenti stack [3], got {vm.stack}"
    elif fname == "010_Incendio.spell":
        assert vm.tape[0] == 5, f"Incendio POST cell=5, got {vm.tape[0]}"
        assert vm.stack == [], "Incendio debe consumir pila"
    elif fname == "011_Evanesco.spell":
        assert vm.stack == [], f"Evanesco POST stack [], got {vm.stack}"
    elif fname == "012_Gemino.spell":
        assert vm.stack == [4,4], f"Gemino POST [4,4], got {vm.stack}"
    elif fname == "013_Expelliarmus.spell":
        assert vm.tape[0] == 3, f"Expelliarmus POST cell=3 (13-10), got {vm.tape[0]}"
        assert vm.stack == [], f"Expelliarmus POST stack [], got {vm.stack}"
    elif fname == "014_Reparo.spell":
        assert vm.tape[0] == 0, f"Reparo POST cell=0, got {vm.tape[0]}"
    elif fname == "015_Muffliato.spell":
        pass  # NOP
    elif fname == "016_Stupefy.spell":
        assert vm.tape[0] == 5, f"Stupefy POST cell=5 (break antes de Nox), got {vm.tape[0]}"
    elif fname == "017_AvadaKedavra.spell":
        assert vm.halted, "AvadaKedavra debe halt"
    else:
        pass

def main():
    fails = []
    for fname, src in sorted(CORPUS.items()):
        path = OUT / fname
        path.write_text(src, encoding="utf-8")
        # verificar parse + run + POST
        try:
            tokens, jumps, breaks = parse_full(src)
            vm = VM()
            inp = b"A" if "Accio" in fname else b""
            vm.reset(tokens, jumps, inp, breaks)
            vm.run()
            _check_post(fname, vm)
        except AssertionError as e:
            fails.append((fname, f"POST fail: {e}"))
        except Exception as e:
            fails.append((fname, str(e)[:180]))

    # Caso especial: Sonorus corpus tiene 2 entradas 008, la segunda sobreescribe la primera — regenera correcta
    # Asegura 17 archivos
    print(f"Generados {len(list(OUT.glob('*.spell')))} .spell en {OUT}/")
    if fails:
        print("FALLOS:")
        for f, e in fails:
            print(f"  {f}: {e}")
        sys.exit(1)
    print("Todos los 17 verificados.")
    # host check
    import subprocess
    for sample in ["001_Lumos.spell", "008_Sonorus.spell", "017_AvadaKedavra.spell"]:
        r = subprocess.run([sys.executable, "host.py", str(OUT / sample)], capture_output=True)
        if r.returncode != 0:
            print(f"host falló {sample}: {r.stderr[:200]}")
            sys.exit(1)
    print("host verifica 3 muestras OK")
    # Verifica que el corpus real tiene 17 archivos distintos (evita duplicado 008)
    assert len(list(OUT.glob("*.spell"))) == 17, "corpus debe ser 17"

if __name__ == "__main__":
    main()
