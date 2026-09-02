# SpellCode

## Qué es

SpellCode es un esolang experimental donde **los hechizos representan
operaciones computacionales**. El lenguaje está inspirado en el universo
mágico de Harry Potter, pero **no es un juego, ni una app, ni una
simulación de Hogwarts** — es una máquina computacional real.

La idea central:

```
hechizo conocido
    ↓
comportamiento
    ↓
concepto computacional
    ↓
abstracción
    ↓
formalización
```

Aprendes programación pensando:

> "Lumos enciende." → "Esto es un incremento."
> "Accio recupera." → "Esto es entrada de datos."
> "Protego bloquea." → "Esto es control de flujo."

y eventualmente descubres:

> "Esto es programación."

## Filosofía

**Comportamiento primero, sintaxis después.**

SpellCode pertenece a una familia de esolangs pedagógicos que usan
dominios familiares como puente hacia la computación formal:

| Lenguaje   | Dominio        | Concepto central        |
|------------|----------------|-------------------------|
| PokéCode   | Pokémon        | Operaciones             |
| DuelCode   | Yu-Gi-Oh!      | Efectos / cadenas       |
| SpellCode  | Harry Potter   | Hechizos / transformaciones |
| JAJAJA     | Humor          | —                       |

Todos comparten la misma progresión:

```
dominio familiar → comportamiento → concepto → abstracción
```

## Máquina

La VM de SpellCode tiene:

```
┌─────────────────────────────────────────────────┐
│  TAPE    — 30 000 celdas de 8 bits (0..255)     │
│  HEAD    — puntero a la celda actual              │
│  PC      — contador de programa (índice)        │
│  STACK   — pila de datos auxiliar                │
│  IN      — cola de bytes de entrada              │
│  OUT     — lista de bytes de salida              │
│  HALT    — flag de parada                        │
└─────────────────────────────────────────────────┘
```

El núcleo de 8 hechizos es equivalente a Brainfuck (y por ende
Turing-completo — ver [TESTURINGS.md](TESTURINGS.md)).

## Hechizos

### Núcleo (Turing-completo)

| Hechizo     | Operación                | Brainfuck | Concepto           |
|-------------|--------------------------|-----------|--------------------|
| Lumos       | cell[head] += 1 (mod 256)| `+`       | Incremento         |
| Nox         | cell[head] -= 1 (mod 256)| `-`       | Decremento         |
| Depulso     | head += 1                | `>`       | Avance de puntero  |
| Levioso     | head -= 1                | `<`       | Retroceso          |
| Protego     | if cell==0 → jump Finite | `[`       | Bucle ( inicio)    |
| Finite      | if cell≠0 → jump Protego | `]`       | Bucle ( fin)       |
| Accio       | cell[head] = read input  | `,`       | Entrada            |
| Sonorus     | write cell[head]         | `.`       | Salida             |

### Extensión (pila de datos)

| Hechizo       | Operación                     | Concepto            |
|---------------|-------------------------------|---------------------|
| Aguamenti     | push cell[head] to stack      | Push a pila         |
| Incendio      | pop stack + add to cell       | Pop + suma          |
| Expelliarmus  | pop stack + sub from cell     | Pop + resta         |
| Evanesco      | pop stack + discard           | Pop + descartar     |
| Gemino        | duplicate stack top           | Duplicación         |

### Extensión (estado y control)

| Hechizo       | Operación                     | Concepto            |
|---------------|-------------------------------|---------------------|
| Reparo        | cell[head] = 0                | Reset               |
| Muffliato     | no operation                  | NOP                 |
| Stupefy       | break innermost loop          | Break               |
| AvadaKedavra  | halt machine                  | Halt / parada       |

## Familias

| Familia          | Hechizos                                |
|------------------|-----------------------------------------|
| Charms           | Lumos, Nox, Depulso, Levioso           |
| Defence          | Protego, Finite, Expelliarmus          |
| Summoning        | Accio, Aguamenti                        |
| Utility          | Sonorus, Muffliato                      |
| Transfiguration  | Evanesco, Gemino, Reparo                |
| DarkArts         | Incendio, Stupefy, AvadaKedavra         |

## Sintaxis

```
# Comentario (empieza con #)
Lumos                # un hechizo por línea
Lumos Sonorus        # o varios separados por espacios
Protego              # los bucles deben estar balanceados
  Lumos
Finite               # como [ y ] en Brainfuck
```

Reglas:
- `#` inicia un comentario hasta fin de línea
- Los espacios y saltos de línea separan hechizos
- Los hechizos son case-sensitive (Lumos, no lumos)
- `Avada Kedavra` y `Finite Incantatem` se aceptan con espacio

## Ejemplos

### Hello World

```bash
spellcode examples/hello.spell
# Salida: Hello World!
```

### Contador (0..4)

```
Lumos Lumos Lumos Lumos Lumos
Protego
  Depulso Sonorus Levioso
  Depulso Lumos Levioso
  Nox
Finite
```

### Condición (if)

```
Accio
Protego
  Depulso
  Lumos
  Levioso
  Reparo
Finite
Depulso
Sonorus
```

### Suma

```bash
echo -n -e '\x03\x04' | spellcode examples/suma.spell
# Salida: byte 0x07
```

### Cat (echo)

```
Accio
Protego
  Sonorus
  Accio
Finite
```

### Pila (Aguamenti + Incendio)

```
Lumos Lumos Lumos
Aguamenti
Nox Nox Nox
Lumos Lumos Lumos Lumos
Aguamenti
Nox Nox Nox Nox
Incendio
Incendio
Sonorus
```

Ver [examples/](examples/) para más ejemplos.

## Ejecución

```bash
# Motor público
python host.py corpus/001_Lumos.spell
python host.py --list
python host.py --all          # 17/17 corpus
python host.py -c "Lumos Sonorus"

# También vía CLI original
spellcode examples/hello.spell
spellcode --dump examples/contador.spell
```

### Corpus canónico `corpus/` — 1 hechizo → 1 ejemplo visible

`corpus/` = **canonical spell examples** (`.spell` fuente + `.spellc` compilado). Cada `.spell`:

- corresponde a **exactamente un hechizo**;
- muestra la **forma mínima válida** de usarlo;
- sirve como **referencia para humanos y LLMs**;
- puede **ejecutarse directamente** con el host (`python host.py corpus/001_Lumos.spell`);
- **NO sustituye** los tests semánticos.

> $$ \boxed{ \text{1 hechizo} \rightarrow \text{1 ejemplo canónico visible} } $$

Para hechizos complejos el ejemplo es una *flashcard ejecutable* con contexto:

```spellcode
# PRE: cell=3
# POST: stack=[3]
Lumos Lumos Lumos
Aguamenti
AvadaKedavra
```

```spellcode
# demonstrate Protego loop
Lumos
Protego
Nox
Finite
AvadaKedavra
```

Separación limpia:

| Carpeta/archivo | Rol |
|---|---|
| `corpus/` | **cómo se usa** |
| `tests/` | **cómo sabemos que funciona** |
| `README` / `TESTURINGS.md` | **qué significa** |
| `host.py` + `spellcode/` | **cómo se ejecuta** |

## Tests

```bash
python -m unittest discover -s tests -v
python host.py --all          # 17/17 corpus
```

57 tests cubren:
- Parser: tokenización, alias, comentarios, errores de sintaxis
- VM: cada hechizo individual, bucles, pila, estado, control
- Compilador BF→SpellCode: mapeo, Hello World, cat, suma
- Tabla de hechizos: resolución, aliases, familias

### Ejemplos funcionales (no maqueta)

Dos programas en `examples/` demuestran cómputo no trivial sin traductor
(la misma idea que en PokéCode/DotaCode/DuelCode, cada uno en su dominio):

| Ejemplo | Archivo | Qué prueba | Salida |
|---------|---------|------------|--------|
| **Fibonacci 10** | `examples/fibonacci.spell` | tape (`Lumos/Nox`), puntero (`Depulso/Levioso`), pila (`Aguamenti/Incendio`), bucles `Protego/Finite` | `0,1,1,2,3,5,8,13,21,34` como bytes (ver con `python -c "print(list(open('out','rb').read()))"` ) |
| **FizzBuzz 1..15** | *(pendiente)* | `MACHOKE` no existe aquí — equivaldría a `Nox`+`Protego` para MOD via restas | — |

```bash
python host.py examples/fibonacci.spell
# -> bytes [0,1,1,2,3,5,8,13,21,34] (+ newline del host)
python -c "import subprocess; print(list(subprocess.check_output(['py','host.py','examples/fibonacci.spell']))[:-1])"
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

# Fibonacci usa stack para c=a+b sin perder a,b:
# Aguamenti (push a) -> Reparo+Incendio (c=a) -> Aguamenti (push b) -> Incendio (c+=b)
```

> **Nota I/O:** SpellCode solo tiene `Sonorus` (byte crudo). Por eso Fibonacci emite bytes `0..34`, no la cadena decimal `"13"` como `MAGIKARP` de PokéCode. La computación es la misma (memoria+pila+bucles), solo cambia el canal de salida.

## TESTURINGS

SpellCode es **Turing-completo**. La demostración está en
[TESTURINGS.md](TESTURINGS.md).

Resumen: los 8 hechizos del núcleo mapean 1:1 a Brainfuck,
que es Turing-completo. Se incluye un compilador `bf_to_spellcode()`
y tests que ejecutan programas Brainfuck reales (Hello World, cat, suma)
traducidos a SpellCode con salida idéntica.

## Limitaciones

- **Cinta finita**: 30 000 celdas (igual que Brainfuck estándar).
  TCP requiere cinta infinita; esto es una restricción de implementación.
- **Límite de pasos**: 10 000 000 (`MAX_STEPS`). Restricción práctica, no teórica.
- **Sin tipos**: todas las celdas son bytes (0..255). No hay strings, floats, etc.
- **Sin funciones/procedimientos**: no hay `call`/`return`. El control de flujo
  es solo bucles (Protego/Finite) y break (Stupefy).
- **Entrada limitada**: la entrada es una secuencia de bytes finita.
  Cuando se agota, Accio devuelve 0.
- **No es interactivo**: la entrada se lee toda al inicio; no hay input interactivo.
- **Pila finita**: 65 536 elementos máximo.
- **Event-driven**: NO implementado. El diseño lo contempló pero se decidió
  que no aportaba al modelo computacional mínimo. La máquina es determinista.
- **Restricciones mágicas (Ministerio)**: NO implementado como capa computacional.
  Se contempló FORBIDDEN/RESTRICTED/ALLOWED pero se consideró lore gratuito
  sin función computacional real.

## Estado experimental

SpellCode es **experimental**. No es producto oficial, no usa logos,
artwork, ni assets propietarios. Los nombres de hechizos se usan únicamente
como inspiración temática para un esolang educativo.

El lenguaje está diseñado para utilizarse en **La Escuela** como puente
pedagógico:

1. "¿Qué hace Lumos?" → "Enciende / incrementa"
2. "¿Qué concepto es?" → "Suma unitaria / incremento"
3. "Formalízalo" → `cell[head] = (cell[head] + 1) % 256`

## Implementación

```
spellcode/
  __init__.py     — API pública (run, parse, VM)
  spells.py        — tabla de hechizos + familias + metadatos
  parser.py        — tokenizer + precompute_jumps (Protego/Finite)
  vm.py            — máquina virtual (tape, head, pc, stack, io)
  cli.py           — CLI ejecutable
  host.py          — motor público todo-en-uno
  corpus/          — 17 ejemplos canónicos (8 núcleo + 9 extensión)
  bf_compiler.py   — traductor Brainfuck → SpellCode (TESTURINGS)
tests/
  test_parser.py   — 17 tests de parser
  test_vm.py       — 26 tests de VM
  test_spells.py   — 9 tests de tabla
  test_bf_compiler.py — 5 tests de TC
examples/
  hello.spell      — Hello World
  cat.spell         — echo
  suma.spell        — suma de 2 bytes
  contador.spell    — cuenta 0..4
  condicion.spell   — if-then
  memoria.spell     — 3 celdas
  io.spell          — invierte 3 chars
  pila.spell        — Aguamenti + Incendio
```

## Uso

```bash
# Instalar
pip install -e .

# Ejecutar un archivo
spellcode examples/hello.spell

# Ejecutar con entrada
echo -n "Test" | spellcode examples/cat.spell

# Código inline
spellcode -c "Lumos Sonorus Nox Sonorus"

# Traducir Brainfuck a SpellCode
spellcode --from-bf --dump programa.bf

# Ver tokens + tabla de saltos
spellcode --dump examples/contador.spell
```

## Licencia

MIT
