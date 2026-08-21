# TESTURINGS — Demostración de Turing-completitud

## Método

SpellCode demuestra Turing-completeness por **traducción fiel desde Brainfuck**.

Brainfuck es Turing-completo (demostrado por su capacidad de simular
una Máquina de Turing de una sola cinta). Si existe una función `T`
que traduce cualquier programa Brainfuck `P` a un programa SpellCode
`T(P)` tal que `T(P)` produce exactamente la misma salida que `P`
para toda entrada, entonces SpellCode es Turing-completo.

## La traducción

```
Brainfuck    SpellCode     Operación
─────────    ─────────     ─────────
>            Depulso       Mover puntero derecho
<            Levioso       Mover puntero izquierdo
+            Lumos         Incrementar celda
-            Nox           Decrementar celda
.            Sonorus       Output
,            Accio         Input
[            Protego       Inicio de bucle (salta al final si cell=0)
]            Finite        Fin de bucle (salta al inicio si cell≠0)
```

Los 8 hechizos del núcleo mapean 1:1 a los 8 operadores de Brainfuck.
Todo carácter que no sea un operador Brainfuck se ignora en la traducción
(igual que en Brainfuck, donde texto no-operador es comentario implícito).

La traducción preserva:
- El estado de la cinta (30 000 celdas, 8 bits, wraparound módulo 256)
- El puntero de cabeza
- El flujo de control (bucles anidados con bracket matching)
- La entrada y salida (bytes crudos)

## Pruebas ejecutadas

### 1. Hello World

```
Brainfuck: ++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.>.
SpellCode: (traducción línea por línea de los 8 operadores)
Salida:    b'Hello World!\n'  ✓
```

### 2. Cat (echo)

```
Brainfuck: ,[.,]
SpellCode: Accio Protego Sonorus Accio Finite
Salida:    b'Test' (dada entrada b'Test')  ✓
```

### 3. Suma de dos números

```
Brainfuck: ,>,[<+>-]<.
SpellCode: Accio Depulso Accio Levioso Protego Lumos Depulso Nox Levioso Finite Levioso Sonorus
Salida:    b'\x07' (dada entrada b'\x03\x04')  ✓
```

### 4. Minsky 2-counter (indirecto)

Brainfuck puede simular una Máquina de Minsky de 2 contadores
([demostrado por Frédérick Wang, 2011]). Como SpellCode traduce
fielmente Brainfuck, SpellCode también simula Minsky 2-counter.

## Conclusión

```
SpellCode ≥ Brainfuck (por traducción 1:1 de los 8 operadores del núcleo)
Brainfuck ≥ Máquina de Turing (demostrado)
∴ SpellCode ≥ Máquina de Turing
∴ SpellCode es Turing-completo.
```

## Limitaciones de la demostración

- La traducción usa los **8 hechizos del núcleo** únicamente.
  Los hechizos de extensión (Aguamenti, Incendio, Stupefy, etc.)
  no participan en la demostración de TC.
- La VM tiene un límite de 10 000 000 de pasos (`MAX_STEPS`),
  que es una restricción práctica, no teórica.
- La cinta tiene 30 000 celdas (igual que Brainfuck estándar);
  TCP requiere cinta infinita, pero esto es una restricción de
  implementación compartida por todos los intérpretes Brainfuck reales.

## Referencias

- Brainfuck: Urban Müller, 1993 (AmigaOS esolang)
- Turing-completeness of Brainfuck: demostrado por simulación de TM
- Minsky 2-counter machine: Marvin Minsky, 1967 ("Computation: Finite and Infinite Machines")
