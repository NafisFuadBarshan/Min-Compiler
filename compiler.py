"""
compiler.py  –  Main entry point
Run:  python compiler.py input.txt
All output files are written to the current working directory.
"""

import sys
import os
from lexer   import Lexer
from parser_ import Parser


def main():
    src = "input.txt"
    if len(sys.argv) > 1:
        src = sys.argv[1]

    if not os.path.exists(src):
        print(f"ERROR: {src} not found")
        sys.exit(1)

    with open(src, "r") as f:
        source_code = f.read()

    print(f"Compiling: {src}")

    # ── Lexing ────────────────────────────────────────────────────────────────
    lexer  = Lexer(source_code)
    tokens = lexer.tokenize()
    lexer.write_tokens("tokens.txt")

    # ── Parsing + all subsequent phases ───────────────────────────────────────
    parser = Parser(tokens)
    parser.parse()
    parser.write_symbol_table("symbol_table.txt")
    parser.write_tac("tac.txt")
    parser.write_parser_output("parser_output.txt")
    parser.write_errors("errors.txt")

    # ── Optimization ──────────────────────────────────────────────────────────
    optimize_tac("tac.txt", "opt.txt")

    # ── Assembly code generation ───────────────────────────────────────────────
    from codegen import CodeGen
    cg = CodeGen(parser.tac_lines, parser.symbol_table)
    cg.generate()
    cg.write("assembly.asm")

    print("\nCompilation Finished")
    print("  tokens.txt, symbol_table.txt, tac.txt, opt.txt,")
    print("  parser_output.txt, errors.txt, assembly.asm  →  written.")


def optimize_tac(infile: str, outfile: str):
    """Remove consecutive duplicate lines (mirrors C optimizeTAC)."""
    try:
        with open(infile) as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"ERROR: {infile} not found")
        return

    with open(outfile, "w") as f:
        f.write("Optimized Intermediate Code\n")
        f.write("---------------------------\n")
        prev = None
        for line in lines[2:]:          # skip header lines
            if line != prev:
                f.write(line)
            prev = line

    print("OPTIMIZATION COMPLETE: opt.txt generated")


if __name__ == "__main__":
    main()
