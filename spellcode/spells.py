"""Tabla de hechizos — el vocabulario de SpellCode.

Cada hechizo mapea a exactamente una operación de la máquina.
El conjunto mínimo (los 8 hechizos del núcleo) es equivalente
a Brainfuck y por ende Turing-completo.  Los hechizos de extensión
añaden una pila de datos y operaciones de control adicionales
para fines pedagógicos, sin alterar la completitud.
"""
from __future__ import annotations

from dataclasses import dataclass

# ── Opcodes del núcleo (Brainfuck-equivalente → TC) ──────────
OP_INC = "inc"               # Lumos
OP_DEC = "dec"               # Nox
OP_RIGHT = "right"           # Depulso
OP_LEFT = "left"             # Levioso
OP_LOOP_START = "loop_start" # Protego
OP_LOOP_END = "loop_end"     # Finite
OP_INPUT = "input"           # Accio
OP_OUTPUT = "output"         # Sonorus

# ── Opcodes de pila ──────────────────────────────────────────
OP_PUSH = "push"             # Aguamenti
OP_POP_ADD = "pop_add"      # Incendio
OP_POP_DISCARD = "pop_disc" # Evanesco
OP_DUP = "dup"              # Gemino
OP_POP_SUB = "pop_sub"      # Expelliarmus

# ── Opcodes de estado ────────────────────────────────────────
OP_ZERO = "zero"            # Reparo
OP_NOP = "nop"              # Muffliato
OP_BREAK = "break"          # Stupefy
OP_HALT = "halt"            # Avada Kedavra

# ── Hechizo → opcode ─────────────────────────────────────────
SPELL_TABLE: dict[str, str] = {
    # Núcleo
    "Lumos":            OP_INC,
    "Nox":              OP_DEC,
    "Depulso":          OP_RIGHT,
    "Levioso":          OP_LEFT,
    "Protego":          OP_LOOP_START,
    "Finite":           OP_LOOP_END,
    "Accio":            OP_INPUT,
    "Sonorus":          OP_OUTPUT,
    # Pila
    "Aguamenti":        OP_PUSH,
    "Incendio":         OP_POP_ADD,
    "Evanesco":         OP_POP_DISCARD,
    "Gemino":           OP_DUP,
    "Expelliarmus":     OP_POP_SUB,
    # Estado
    "Reparo":           OP_ZERO,
    "Muffliato":        OP_NOP,
    "Stupefy":          OP_BREAK,
    "AvadaKedavra":     OP_HALT,
}

OPCODE_TO_SPELL: dict[str, str] = {v: k for k, v in SPELL_TABLE.items()}

# Alias: "Avada Kedavra" (con espacio) también se acepta
_ALIASES: dict[str, str] = {
    "Avada Kedavra": "AvadaKedavra",
    "avada kedavra": "AvadaKedavra",
    "Finite Incantatem": "Finite",
}
SPELL_ALIASES: dict[str, str] = {**_ALIASES}


# ── Metadatos pedagógicos ────────────────────────────────────
@dataclass(frozen=True, slots=True)
class SpellInfo:
    name: str
    opcode: str
    family: str
    behavior: str       # qué hace (en español)
    concept: str        # concepto computacional que representa


SPELL_REGISTRY: dict[str, SpellInfo] = {
    "Lumos": SpellInfo("Lumos", OP_INC, "Charms",
        "Incrementa la celda apuntada en 1 (módulo 256).",
        "Suma unitaria / incremento."),
    "Nox": SpellInfo("Nox", OP_DEC, "Charms",
        "Decrementa la celda apuntada en 1 (módulo 256).",
        "Resta unitaria / decremento."),
    "Depulso": SpellInfo("Depulso", OP_RIGHT, "Charms",
        "Mueve el puntero de memoria a la derecha (+1).",
        "Avance de puntero / dirección de memoria."),
    "Levioso": SpellInfo("Levioso", OP_LEFT, "Charms",
        "Mueve el puntero de memoria a la izquierda (-1).",
        "Retroceso de puntero / dirección de memoria."),
    "Protego": SpellInfo("Protego", OP_LOOP_START, "Defence",
        "Si la celda actual es 0, salta al hechizo Finite emparejado.",
        "Bucle condicional / branch-if-zero (opening bracket)."),
    "Finite": SpellInfo("Finite", OP_LOOP_END, "Defence",
        "Si la celda actual no es 0, salta de vuelta al Protego emparejado.",
        "Cierre de bucle / branch-if-nonzero (closing bracket)."),
    "Accio": SpellInfo("Accio", OP_INPUT, "Summoning",
        "Lee un byte de la entrada y lo guarda en la celda actual. "
        "Si no hay más entrada, la celda queda en 0.",
        "Entrada / lectura de stdin."),
    "Sonorus": SpellInfo("Sonorus", OP_OUTPUT, "Utility",
        "Escribe el valor de la celda actual a la salida como byte.",
        "Salida / escritura a stdout."),
    "Aguamenti": SpellInfo("Aguamenti", OP_PUSH, "Summoning",
        "Empuja el valor de la celda actual a la pila de datos.",
        "Push a pila / generación de flujo de datos."),
    "Incendio": SpellInfo("Incendio", OP_POP_ADD, "DarkArts",
        "Saca el tope de la pila y lo suma a la celda actual.",
        "Pop + add / consumo de dato."),
    "Evanesco": SpellInfo("Evanesco", OP_POP_DISCARD, "Transfiguration",
        "Saca el tope de la pila y lo descarta.",
        "Pop + descartar / liberación de recurso."),
    "Gemino": SpellInfo("Gemino", OP_DUP, "Transfiguration",
        "Duplica el tope de la pila (si la pila no está vacía).",
        "Duplicación de dato / copia."),
    "Expelliarmus": SpellInfo("Expelliarmus", OP_POP_SUB, "Defence",
        "Saca el tope de la pila y lo resta de la celda actual.",
        "Pop + sub / eliminación de valor."),
    "Reparo": SpellInfo("Reparo", OP_ZERO, "Transfiguration",
        "Establece la celda actual en 0.",
        "Reset / estado inicial."),
    "Muffliato": SpellInfo("Muffliato", OP_NOP, "Utility",
        "No hace nada.",
        "NOP / operación nula."),
    "Stupefy": SpellInfo("Stupefy", OP_BREAK, "DarkArts",
        "Rompe el bucle más interno: salta al Finite emparejado +1.",
        "Break / salida de bucle."),
    "AvadaKedavra": SpellInfo("AvadaKedavra", OP_HALT, "DarkArts",
        "Detiene la máquina inmediatamente.",
        "Halt / parada del programa."),
}

# Núcleo TC (los 8 que mapean a Brainfuck)
CORE_SPELLS: frozenset[str] = frozenset({
    "Lumos", "Nox", "Depulso", "Levioso",
    "Protego", "Finite", "Accio", "Sonorus",
})

FAMILIES: dict[str, tuple[str, ...]] = {
    "Charms":        ("Lumos", "Nox", "Depulso", "Levioso"),
    "Defence":       ("Protego", "Finite", "Expelliarmus"),
    "Summoning":     ("Accio", "Aguamenti"),
    "Utility":       ("Sonorus", "Muffliato"),
    "Transfiguration": ("Evanesco", "Gemino", "Reparo"),
    "DarkArts":      ("Incendio", "Stupefy", "AvadaKedavra"),
}


def resolve(name: str) -> str | None:
    """Resuelve un token a su nombre canónico de hechizo, o None."""
    if name in SPELL_TABLE:
        return name
    if name in SPELL_ALIASES:
        return SPELL_ALIASES[name]
    return None
