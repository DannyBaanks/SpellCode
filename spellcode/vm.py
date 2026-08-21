"""Máquina virtual de SpellCode.

Estado de la máquina:
  ┌─────────────────────────────────────────────┐
  │  TAPE   — 30 000 celdas de 8 bits (0..255)   │
  │  HEAD   — puntero a la celda actual           │
  │  PC     — contador de programa (índice)      │
  │  STACK  — pila de datos auxiliar              │
  │  IN     — cola de bytes de entrada            │
  │  OUT    — lista de bytes de salida            │
  │  FLAGS  — (halt, )                            │
  └─────────────────────────────────────────────┘

El núcleo de 8 hechizos mapea 1:1 a Brainfuck:
  Depulso  →  >    (right)
  Levioso →  <    (left)
  Lumos   →  +    (inc)
  Nox     →  -    (dec)
  Sonorus →  .    (output)
  Accio   →  ,    (input)
  Protego →  [    (loop start)
  Finite  →  ]    (loop end)

Los hechizos de extensión añaden una pila de datos y
operaciones de estado, sin romper la equivalencia con Brainfuck.
"""
from __future__ import annotations

from .spells import (
    SPELL_TABLE,
    OP_INC, OP_DEC, OP_RIGHT, OP_LEFT,
    OP_LOOP_START, OP_LOOP_END,
    OP_INPUT, OP_OUTPUT,
    OP_PUSH, OP_POP_ADD, OP_POP_DISCARD, OP_DUP, OP_POP_SUB,
    OP_ZERO, OP_NOP, OP_BREAK, OP_HALT,
)

TAPE_SIZE = 30_000
MAX_STEPS = 10_000_000
STACK_LIMIT = 65_536


class SpellCodeError(Exception):
    """Error de ejecución de la VM."""


class VM:
    __slots__ = (
        "tape", "head", "pc", "stack",
        "input_buf", "input_pos", "output", "halted",
        "steps", "jump_table", "break_table", "tokens",
        "_loop_depth",
    )

    def __init__(self) -> None:
        self.tape: bytearray = bytearray(TAPE_SIZE)
        self.head: int = 0
        self.pc: int = 0
        self.stack: list[int] = []
        self.input_buf: bytes = b""
        self.input_pos: int = 0
        self.output: bytearray = bytearray()
        self.halted: bool = False
        self.steps: int = 0
        self.jump_table: list[int] = []
        self.break_table: list[int] = []
        self.tokens: list[str] = []
        self._loop_depth: int = 0

    def reset(self, tokens: list[str], jump_table: list[int],
              input_data: bytes = b"",
              break_table: list[int] | None = None) -> None:
        self.tape = bytearray(TAPE_SIZE)
        self.head = 0
        self.pc = 0
        self.stack = []
        self.input_buf = input_data
        self.input_pos = 0
        self.output = bytearray()
        self.halted = False
        self.steps = 0
        self.jump_table = jump_table
        self.break_table = break_table if break_table is not None else [-1] * len(tokens)
        self.tokens = tokens
        self._loop_depth = 0

    def read_input(self) -> int:
        """Lee el siguiente byte de entrada. Si no hay, devuelve 0."""
        if self.input_pos < len(self.input_buf):
            b = self.input_buf[self.input_pos]
            self.input_pos += 1
            return b
        return 0

    def step(self) -> bool:
        """Ejecuta una instrucción. Devuelve False si el programa terminó."""
        if self.halted or self.pc >= len(self.tokens):
            return False
        if self.steps >= MAX_STEPS:
            raise SpellCodeError(f"Superado límite de {MAX_STEPS} pasos")
        self.steps += 1

        tok = self.tokens[self.pc]
        op = SPELL_TABLE.get(tok, OP_NOP)
        t = self.tape
        h = self.head

        if op == OP_INC:
            t[h] = (t[h] + 1) & 0xFF
        elif op == OP_DEC:
            t[h] = (t[h] - 1) & 0xFF
        elif op == OP_RIGHT:
            if h + 1 >= TAPE_SIZE:
                raise SpellCodeError("Desbordamiento de memoria: Depulso al límite derecho")
            self.head = h + 1
        elif op == OP_LEFT:
            if h == 0:
                raise SpellCodeError("Desbordamiento de memoria: Levioso al límite izquierdo")
            self.head = h - 1
        elif op == OP_OUTPUT:
            self.output.append(t[h])
        elif op == OP_INPUT:
            t[h] = self.read_input() & 0xFF
        elif op == OP_LOOP_START:
            if t[h] == 0:
                self.pc = self.jump_table[self.pc]
            else:
                self._loop_depth += 1
        elif op == OP_LOOP_END:
            if t[h] != 0:
                self.pc = self.jump_table[self.pc]
            else:
                self._loop_depth -= 1
        elif op == OP_PUSH:
            self.stack.append(t[h])
            if len(self.stack) > STACK_LIMIT:
                raise SpellCodeError("Pila desbordada: Aguamenti excedió el límite")
        elif op == OP_POP_ADD:
            if not self.stack:
                raise SpellCodeError("Pila vacía: Incendio no tiene datos")
            t[h] = (t[h] + self.stack.pop()) & 0xFF
        elif op == OP_POP_SUB:
            if not self.stack:
                raise SpellCodeError("Pila vacía: Expelliarmus no tiene datos")
            t[h] = (t[h] - self.stack.pop()) & 0xFF
        elif op == OP_POP_DISCARD:
            if not self.stack:
                raise SpellCodeError("Pila vacía: Evanesco no tiene datos")
            self.stack.pop()
        elif op == OP_DUP:
            if not self.stack:
                raise SpellCodeError("Pila vacía: Gemino no tiene datos")
            self.stack.append(self.stack[-1])
            if len(self.stack) > STACK_LIMIT:
                raise SpellCodeError("Pila desbordada: Gemino excedió el límite")
        elif op == OP_ZERO:
            t[h] = 0
        elif op == OP_NOP:
            pass
        elif op == OP_BREAK:
            target = self.break_table[self.pc]
            if target == -1:
                raise SpellCodeError("Stupefy fuera de un Protego/Finite")
            self.pc = target + 1
            self._loop_depth -= 1
            return True
        elif op == OP_HALT:
            self.halted = True
            return False

        self.pc += 1
        return True

    def run(self) -> bytes:
        """Ejecuta hasta terminar. Devuelve la salida como bytes."""
        while self.step():
            pass
        return bytes(self.output)
