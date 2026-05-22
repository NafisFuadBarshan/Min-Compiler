# 🛠️ Python Mini Compiler

A complete, educational compiler pipeline built from scratch in Python — supporting a simplified C-like language with lexing, parsing, semantic analysis, TAC generation, optimization, and pseudo-assembly code generation.

---

## 📖 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Compiler Pipeline](#compiler-pipeline)
- [Supported Language Syntax](#supported-language-syntax)
- [Getting Started](#getting-started)
- [Output Files](#output-files)
- [Example](#example)
- [Limitations](#limitations)
- [Future Work](#future-work)
- [License](#license)

---

## Overview

This project implements all classical stages of a compiler entirely in Python, without any external parser or lexer generators. It mirrors the behaviour of a traditional C-language toolchain built with **Flex** and **Bison**, but is written in pure Python for portability and educational clarity.

The compiler accepts a simplified C-like language and produces human-readable output at every stage, making it ideal for learning how compilers work from source code all the way to assembly.

---

## Features

- ✅ **Lexical Analysis** — tokenises source code into a typed token stream
- ✅ **Recursive-Descent Parser** — hand-written, mirrors a Bison grammar
- ✅ **Symbol Table** — tracks variable names, types, sizes, and memory addresses
- ✅ **Semantic Analysis** — detects redeclaration and use-before-declaration errors
- ✅ **Three-Address Code (TAC) Generation** — classic intermediate representation
- ✅ **Constant Folding** — evaluates constant expressions at compile time
- ✅ **Peephole Optimization** — eliminates consecutive duplicate TAC instructions
- ✅ **Pseudo-Assembly Generation** — produces readable assembly-like output
- ✅ **Error Reporting** — syntax and semantic errors with source-line numbers

---

## Project Structure

```
mini-compiler/
│
├── compiler.py       # Entry point — orchestrates all compilation stages
├── lexer.py          # Lexical analyser — tokenises source code
├── parser_.py        # Recursive-descent parser + TAC + symbol table
├── codegen.py        # Assembly code generator from TAC
├── input.txt         # Sample source file
│
└── outputs/          # Generated after running the compiler
    ├── tokens.txt
    ├── symbol_table.txt
    ├── tac.txt
    ├── opt.txt
    ├── parser_output.txt
    ├── errors.txt
    └── assembly.asm
```

---

## Compiler Pipeline

```
Source Code (input.txt)
        │
        ▼
┌───────────────────┐
│   Lexer (lexer.py)│  →  tokens.txt
└────────┬──────────┘
         │ Token Stream
         ▼
┌──────────────────────┐
│  Parser (parser_.py) │  →  symbol_table.txt
│  + Semantic Analysis │  →  parser_output.txt
│  + TAC Generation    │  →  tac.txt
│                      │  →  errors.txt
└──────────┬───────────┘
           │ TAC Lines
           ▼
┌────────────────────────────┐
│  Optimizer (compiler.py)   │  →  opt.txt
└────────────┬───────────────┘
             │ Optimized TAC
             ▼
┌──────────────────────────┐
│  Code Gen (codegen.py)   │  →  assembly.asm
└──────────────────────────┘
```

---

## Supported Language Syntax

The compiler supports the following constructs:

### Variable Declaration
```c
int x;
int y = 10;
```

### Assignment
```c
x = y + 5;
```

### Arithmetic Operators
```
+   -   *   /
```

### Relational Operators
```
>   <   >=   <=   ==   !=
```

### If / Else
```c
if (x > 10) {
    print(x);
} else {
    print(y);
}
```

### While Loop
```c
while (x < y) {
    x = x + 1;
}
```

### Print
```c
print(z);
```

---

## Getting Started

### Prerequisites

- Python **3.10** or later
- No external dependencies required

### Installation

```bash
git clone https://github.com/your-username/mini-compiler.git
cd mini-compiler
```

### Running the Compiler

```bash
# Compile the default input.txt
python compiler.py

# Compile a custom source file
python compiler.py myprogram.txt
```

### Expected Console Output

```
Compiling: input.txt
OPTIMIZATION COMPLETE: opt.txt generated

Compilation Finished
  tokens.txt, symbol_table.txt, tac.txt, opt.txt,
  parser_output.txt, errors.txt, assembly.asm  →  written.
```

---

## Output Files

| File | Description |
|---|---|
| `tokens.txt` | All tokens with their type and lexeme |
| `symbol_table.txt` | Variables: name, type, size, dim, line, address |
| `tac.txt` | Three-address intermediate code |
| `opt.txt` | Optimized TAC (duplicate lines removed) |
| `parser_output.txt` | Grammar rules matched during parsing |
| `errors.txt` | All syntax and semantic errors |
| `assembly.asm` | Final pseudo-assembly output |

---

## Example

**Input (`input.txt`):**
```c
int x = 10;
int y = 20;
int z;

z = x + y;

if(z > 20) {
    print(z);
}

while(x < y) {
    x = x + 1;
}
```

**Symbol Table (`symbol_table.txt`):**
```
Name    Type    Size    Dim    Line    Address
---------------------------------------------
x       int     4       0      1       1000
y       int     4       0      2       1004
z       int     4       0      3       1008
```

**Three-Address Code (`tac.txt`):**
```
Three Address Code
------------------
x = 10
y = 20
t0 = x + y
z = t0
t1 = z > 20
IF_FALSE t1 GOTO L0
PRINT z
LABEL L0
LABEL L2
t2 = x < y
IF_FALSE t2 GOTO L3
t3 = x + 1
x = t3
GOTO L2
LABEL L3
```

**Assembly Output (`assembly.asm`):**
```asm
Assembly Code
-------------
DECLARE x
DECLARE y
DECLARE z
MOV R0, 10
MOV x, R0
MOV R0, 20
MOV y, R0
MOV R0, x
ADD R0, y
MOV t0, R0
MOV R0, t0
MOV z, R0
CMP z, 20
SETGT t1
CMP t1, 0
JE L0
PRINT z
L0:
...
```

---

## Limitations

- Only the `int` data type is supported
- No functions, recursion, or variable scoping
- Optimization is limited to consecutive-duplicate elimination
- Assembly output is pseudo-assembly — no real binary is generated
- Error recovery is minimal (single-token panic mode)

---

## Future Work

- [ ] Support `float`, `char`, and array types
- [ ] Add function declarations and calls
- [ ] Implement advanced optimizations (constant propagation, CSE, dead-code elimination)
- [ ] Target a real ISA (x86-64 or ARM)
- [ ] Build a two-pass assembler to emit binary machine code
- [ ] Add a proper scope manager for nested blocks

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

> Built as a Compiler Design course project. Contributions and suggestions are welcome!
