# C Compiler User Guide

## Table of Contents
1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Quick Start](#quick-start)
4. [Detailed Usage](#detailed-usage)
5. [Compiler Phases](#compiler-phases)
6. [Output Files](#output-files)
7. [Examples](#examples)
8. [Troubleshooting](#troubleshooting)
9. [Language Features](#language-features)
10. [Architecture](#architecture)

---

## Overview

This is a multi-phase compiler for a C-like language implemented in Python. It processes source code through:
- **Lexical Analysis** (Tokenization)
- **Syntax Analysis** (Parsing)
- **Three-Address Code (TAC) Generation**
- **Optimization**
- **Assembly Code Generation**

All phases work together to produce assembly code from C-like source programs.

---

## Installation & Setup

### Requirements
- Python 3.8 or higher
- No external dependencies required

### Files Provided
```
lexer.py        - Lexical analyzer
parser_.py      - Parser and semantic analyzer
codegen.py      - Code generator
compiler.py     - Main compiler driver
input.txt       - Sample input file
```

### Setup Steps
1. Place all `.py` files in the same directory
2. Create your C program in `input.txt` or another file
3. Run the compiler

---

## Quick Start

### Basic Command
```bash
python3 compiler.py
```
This compiles `input.txt` (default file).

### Compile Specific File
```bash
python3 compiler.py myprogram.c
```

### Expected Output
```
Compiling: input.txt
Phase 1: Lexical Analysis...
  ✓ Found 46 tokens
Phase 2: Syntax Analysis and Parsing...
  ✓ Parsing successful
  ✓ Symbol table: 3 variables
  ✓ Generated 15 TAC instructions
Phase 3: Optimization...
  ✓ TAC optimization complete
Phase 4: Code Generation...
  ✓ Assembly code generation complete

==================================================
Compilation Finished Successfully!
==================================================
```

---

## Detailed Usage

### Command-Line Interface

#### Basic Compilation
```bash
python3 compiler.py input.txt
```

#### Help/Info
```bash
python3 compiler.py
python3 compiler.py --help
```

### Module-by-Module Testing

#### Test Lexer Only
```bash
python3 lexer.py
# Produces: tokens.txt
```

#### Test Parser Only
```bash
python3 parser_.py
# Produces: symbol_table.txt, tac.txt, parser_output.txt, errors.txt
```

#### Test Code Generator Only
```bash
python3 codegen.py
# Produces: assembly.asm
```

#### Run Full Compiler
```bash
python3 compiler.py
# Produces: all output files
```

---

## Compiler Phases

### Phase 1: Lexical Analysis
**Input**: Source code text  
**Output**: tokens.txt  
**Function**: Converts source code into tokens

```
Input:  int x = 10;
Output: 
  Keyword    int
  Identifier x
  Assignment =
  Number     10
  Punctuation ;
```

### Phase 2: Syntax Analysis & Parsing
**Input**: Tokens from Phase 1  
**Output**: symbol_table.txt, tac.txt, parser_output.txt, errors.txt  
**Function**: 
- Builds symbol table of variables
- Generates three-address code
- Records grammar rule matches
- Detects and reports errors

```
Three-Address Code:
  x = 10
  y = 20
  t0 = x + y
  z = t0
```

### Phase 3: Optimization
**Input**: tac.txt  
**Output**: opt.txt  
**Function**: Removes redundant instructions

```
Optimization: Removed N duplicate instructions
```

### Phase 4: Code Generation
**Input**: TAC from Phase 2, Symbol table  
**Output**: assembly.asm  
**Function**: Converts TAC to assembly instructions

```
Assembly:
  DECLARE x
  MOV x, 10
  DECLARE y
  MOV y, 20
```

---

## Output Files

### 1. tokens.txt
**Purpose**: Lists all tokens found in source code  
**Format**:
```
Token Type       Lexeme
---------        ------
Keyword          int
Identifier       x
Assignment       =
Number           10
Punctuation      ;
```

### 2. symbol_table.txt
**Purpose**: Shows all declared variables with metadata  
**Format**:
```
Name  Type  Size  Dim  Line  Address
----  ----  ----  ---  ----  -------
x     int   4     0    1     1000
y     int   4     0    2     1004
z     int   4     0    3     1008
```

**Fields Explained**:
- **Name**: Variable name
- **Type**: Data type (int)
- **Size**: Size in bytes
- **Dim**: Array dimension (0 = not array)
- **Line**: Line number in source
- **Address**: Memory address

### 3. tac.txt
**Purpose**: Three-Address Code intermediate representation  
**Format**:
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
```

**TAC Instructions**:
- **Assignment**: `var = expr`
- **Binary Op**: `temp = var1 op var2`
- **Unary Op**: `temp = op var`
- **Conditional Jump**: `IF_FALSE temp GOTO label`
- **Unconditional Jump**: `GOTO label`
- **Label**: `LABEL name`
- **Print**: `PRINT expr`

### 4. opt.txt
**Purpose**: Optimized TAC with duplicate removal  
**Format**: Same as TAC but with consecutive duplicates removed

### 5. parser_output.txt
**Purpose**: Grammar rules matched during parsing  
**Format**:
```
Grammar Rules Matched
---------------------
program -> statements
statements -> statement
declaration -> int id = expression ;
expression -> term
term -> factor
factor -> number
...
```

### 6. errors.txt
**Purpose**: Syntax and semantic errors found  
**Format**:
```
Error List
----------
Syntax Error line 5: expected Punctuation(';') got EOF
Semantic Error line 3: x redeclared
Semantic Error line 8: y not declared
```

### 7. assembly.asm
**Purpose**: Final assembly code output  
**Format**:
```
Assembly Code
-------------
DECLARE x
DECLARE y
DECLARE z
MOV x, 10
MOV y, 20
MOV R0, x
ADD R0, y
MOV t0, R0
MOV t1, x
MOV z, t1
...
```

**Assembly Instructions**:
- **MOV**: Move/Load data
- **ADD**: Addition
- **SUB**: Subtraction
- **MUL**: Multiplication
- **DIV**: Division
- **MOD**: Modulo
- **CMP**: Compare
- **JE**: Jump if Equal
- **JMP**: Unconditional Jump
- **SETGT/SETLT/etc**: Set on comparison
- **PRINT**: Output value
- **LABEL**: Code label

---

## Examples

### Example 1: Simple Variable Declaration

**Input (input.txt)**:
```c
int x = 10;
int y = 20;
int z;
z = x + y;
print(z);
```

**TAC Output**:
```
x = 10
y = 20
t0 = x + y
z = t0
PRINT z
```

**Assembly Output**:
```
DECLARE x
DECLARE y
DECLARE z
MOV x, 10
MOV y, 20
MOV R0, x
ADD R0, y
MOV t0, R0
MOV R0, t0
MOV z, R0
PRINT z
```

---

### Example 2: If Statement

**Input**:
```c
int x = 5;
if(x > 3)
{
    print(x);
}
```

**TAC Output**:
```
x = 5
t0 = x > 3
IF_FALSE t0 GOTO L0
PRINT x
LABEL L0
```

**Assembly Output**:
```
DECLARE x
MOV x, 5
CMP x, 3
SETGT t0
CMP t0, 0
JE L0
PRINT x
L0:
```

---

### Example 3: While Loop

**Input**:
```c
int i = 0;
int sum = 0;
while(i < 5)
{
    sum = sum + i;
    i = i + 1;
}
```

**TAC Output**:
```
i = 0
sum = 0
LABEL L0
t0 = i < 5
IF_FALSE t0 GOTO L1
t1 = sum + i
sum = t1
t2 = i + 1
i = t2
GOTO L0
LABEL L1
```

---

### Example 4: Complex Expression

**Input**:
```c
int a = 10;
int b = 20;
int c;
c = a + b * 2;
```

**TAC Output** (note: operator precedence):
```
a = 10
b = 20
t0 = b * 2
t1 = a + t0
c = t1
```

**Assembly Output**:
```
DECLARE a
DECLARE b
DECLARE c
MOV a, 10
MOV b, 20
MOV R0, b
MUL R0, 2
MOV t0, R0
MOV R0, a
ADD R0, t0
MOV t1, R0
MOV R0, t1
MOV c, R0
```

---

## Troubleshooting

### Problem: "ERROR: input.txt not found"
**Solution**: Create `input.txt` in the current directory or specify correct path
```bash
python3 compiler.py /path/to/your/file.c
```

### Problem: Syntax errors in errors.txt
**Solution**: Review your source code for:
- Missing semicolons
- Mismatched brackets
- Incorrect keyword usage

### Problem: Undefined variable errors
**Solution**: Declare all variables before use
```c
int x;  // Declare first
x = 10; // Then use
```

### Problem: Division by zero warnings
**Note**: The compiler performs constant folding but doesn't check for runtime errors. Be careful with constant expressions.

### Problem: No output files generated
**Solution**: 
1. Check that all Python files are in same directory
2. Ensure input.txt exists and is readable
3. Check for Python version compatibility (Python 3.8+)

---

## Language Features

### Supported Data Types
- `int` - 32-bit integer

### Supported Operators

**Arithmetic**:
- `+` Addition
- `-` Subtraction
- `*` Multiplication
- `/` Division
- `%` Modulo

**Relational**:
- `>` Greater than
- `<` Less than
- `>=` Greater or equal
- `<=` Less or equal
- `==` Equal
- `!=` Not equal

**Assignment**:
- `=` Assignment

### Supported Statements

**Declaration**:
```c
int x;              // Declare
int y = 10;         // Declare and initialize
```

**Assignment**:
```c
x = 5;              // Simple assignment
x = y + 10;         // Expression assignment
```

**Output**:
```c
print(x);           // Print variable
print(x + 10);      // Print expression
```

**Control Flow**:
```c
if(condition) {     // If statement
    // statements
}

if(condition) {     // If-else statement
    // statements
} else {
    // statements
}

while(condition) {  // While loop
    // statements
}
```

### Unsupported Features
- Functions/procedures
- Arrays
- Pointers
- Structs
- String literals
- Comments (except in code)
- Multiple statements on one line
- Do-while loops
- For loops
- Switch statements
- Break/continue

---

## Architecture

### Module Structure

```
┌─────────────────────┐
│   Source Code       │
│   (input.txt)       │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────┐
│   Lexer (lexer.py)   │ ─→ tokens.txt
│   Tokenization       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Parser (parser_.py) │ ─→ symbol_table.txt
│  Symbol Table        │    tac.txt
│  TAC Generation      │    parser_output.txt
│  Error Checking      │    errors.txt
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Optimizer            │ ─→ opt.txt
│ Duplicate Removal    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│CodeGen (codegen.py)  │ ─→ assembly.asm
│Assembly Generation   │
└──────────────────────┘
```

### Data Flow

```
Tokens
  ▼
Symbol Table + TAC
  ▼
Optimized TAC
  ▼
Assembly Code
```

### Key Classes

**Token** (lexer.py):
- `kind`: Token type (Keyword, Identifier, etc.)
- `lexeme`: Token text
- `line`: Source line number

**Symbol** (parser_.py):
- `name`: Variable name
- `type_`: Data type
- `size`: Size in bytes
- `dim`: Array dimension
- `line`: Declaration line
- `address`: Memory address

**Lexer** (lexer.py):
- `tokenize()`: Convert source to tokens
- `write_tokens(path)`: Write tokens to file

**Parser** (parser_.py):
- `parse()`: Parse tokens
- `symbol_table`: List of Symbol objects
- `tac_lines`: List of TAC instructions
- `errors`: List of error messages

**CodeGen** (codegen.py):
- `generate()`: Generate assembly code
- `write(path)`: Write assembly to file

---

## Performance Notes

- Lexer: O(n) where n = source code length
- Parser: O(n) where n = number of tokens
- Optimizer: O(m) where m = number of TAC lines
- Code Generator: O(m) where m = number of TAC lines

Overall: O(n) performance on input size

---

## Version Information

- **Language**: C-like subset
- **Python Version**: 3.8+
- **Last Updated**: 2026
- **Status**: Stable

---

## Support & Feedback

For issues or suggestions:
1. Check the Troubleshooting section
2. Review the compiler output files
3. Verify your input syntax
4. Test with the provided examples

---

Happy Compiling! 🚀
