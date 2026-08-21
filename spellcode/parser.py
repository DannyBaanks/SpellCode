"""Parser de SpellCode.

Tokeniza líneas de hechizos y resuelve alias, comentarios y
estructura de bucles (Protego/Finite emparejados).

Formato de un programa:
    - Un hechizo por línea, o varios separados por espacios.
    - Líneas que empiezan con # son comentarios.
    - Se ignoran líneas en blanco.
    - Protego y Finite deben estar balanceados (como [ y ] en Brainfuck).
"""
from __future__ import annotations

from .spells import OP_LOOP_END, OP_LOOP_START, resolve


class SpellCodeParseError(Exception):
    """Error de sintaxis en un programa SpellCode."""


def tokenize(source: str) -> list[str]:
    """Convierte texto fuente en una lista de nombres de hechizo canónicos.

    Reglas:
      - # inicia comentario (hasta fin de línea)
      -Whitespace separa tokens
      - Se resuelven alias (ej. "Avada Kedavra" → "AvadaKedavra")
      - Se aceptan hechizos multi-palabra Unidos por espacio
    """
    tokens: list[str] = []
    lines = source.splitlines()

    for line_no, raw in enumerate(lines, 1):
        # Strip comment
        text = raw.split("#", 1)[0].strip()
        if not text:
            continue

        words = text.split()
        i = 0
        unknown: list[str] = []

        while i < len(words):
            # Intentar match de longest alias (hasta 3 palabras)
            matched = False
            for length in (3, 2, 1):
                if i + length <= len(words):
                    candidate = " ".join(words[i:i + length])
                    canonical = resolve(candidate)
                    if canonical is not None:
                        tokens.append(canonical)
                        i += length
                        matched = True
                        break
            if not matched:
                unknown.append(words[i])
                i += 1

        if unknown:
            raise SpellCodeParseError(
                f"Línea {line_no}: hechizo(s) desconocido(s): {unknown}"
            )

    return tokens


def precompute_jumps(tokens: list[str]) -> tuple[list[int], list[int]]:
    """Calcula los saltos de Protego/Finite y la tabla de break (Stupefy).

    Devuelve (jump_table, break_table) donde:
      - jump_table[i]: para Protego → Finite emparejado; para Finite → Protego.
      - break_table[i]: índice del Finite que cierra el bucle más interno
        que contiene la posición i (para Stupefy). -1 si no hay bucle.
    """
    from .spells import SPELL_TABLE

    jump_table = [-1] * len(tokens)
    break_table = [-1] * len(tokens)
    stack: list[int] = []

    # Primera pasada: emparejar Protego/Finite
    for i, tok in enumerate(tokens):
        op = SPELL_TABLE.get(tok, "")
        if op == OP_LOOP_START:
            stack.append(i)
        elif op == OP_LOOP_END:
            if not stack:
                raise SpellCodeParseError(
                    f"Finite sin Protego emparejado (índice {i})"
                )
            start = stack.pop()
            jump_table[start] = i
            jump_table[i] = start

    if stack:
        raise SpellCodeParseError(
            f"Protego sin Finite emparejado (índice {stack[-1]})"
        )

    # Segunda pasada: break_table
    open_loops: list[int] = []  # índices de Protego sin cerrar
    for i, tok in enumerate(tokens):
        op = SPELL_TABLE.get(tok, "")
        if op == OP_LOOP_START:
            break_table[i] = jump_table[i]
            open_loops.append(i)
        elif op == OP_LOOP_END:
            break_table[i] = i
            if open_loops:
                open_loops.pop()
        else:
            if open_loops:
                break_table[i] = jump_table[open_loops[-1]]

    return jump_table, break_table


def parse(source: str) -> tuple[list[str], list[int]]:
    """Tokeniza + precomputa saltos.

    Devuelve (tokens, jump_table).
    La break_table se obtiene con precompute_jumps directamente.
    """
    tokens = tokenize(source)
    jumps, _breaks = precompute_jumps(tokens)
    return tokens, jumps


def parse_full(source: str) -> tuple[list[str], list[int], list[int]]:
    """Tokeniza + precomputa jump_table y break_table.

    Devuelve (tokens, jump_table, break_table).
    """
    tokens = tokenize(source)
    jumps, breaks = precompute_jumps(tokens)
    return tokens, jumps, breaks
