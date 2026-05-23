import sys
import os
from lexer   import Lexer
from parser_ import Parser
from codegen import CodeGen


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
    print("Phase 1: Lexical Analysis...")
    lexer  = Lexer(source_code)
    tokens = lexer.tokenize()
    lexer.write_tokens("tokens.txt")
    print(f"  ✓ Found {len(tokens)} tokens")

    # ── Parsing + all subsequent phases ───────────────────────────────────────
    print("Phase 2: Syntax Analysis and Parsing...")
    parser = Parser(tokens)
    parser.parse()
    parser.write_symbol_table("symbol_table.txt")
    parser.write_tac("tac.txt")
    parser.write_parser_output("parser_output.txt")
    parser.write_errors("errors.txt")
    
    # Check for parse errors
    if parser.errors:
        print(f"  ⚠ {len(parser.errors)} errors found")
        for error in parser.errors:
            print(f"    - {error}")
    else:
        print("  ✓ Parsing successful")
    
    print(f"  ✓ Symbol table: {len(parser.symbol_table)} variables")
    print(f"  ✓ Generated {len(parser.tac_lines)} TAC instructions")

    # ── Optimization ──────────────────────────────────────────────────────────
    print("Phase 3: Optimization...")
    optimize_tac("tac.txt", "opt.txt")
    print("  ✓ TAC optimization complete")

    # ── Assembly code generation ───────────────────────────────────────────────
    print("Phase 4: Code Generation...")
    cg = CodeGen(parser.tac_lines, parser.symbol_table)
    cg.generate()
    cg.write("assembly.asm")
    print("  ✓ Assembly code generation complete")

    print("\n" + "="*50)
    print("Compilation Finished Successfully!")
    print("="*50)
    print("\nGenerated Files:")
    print("  • tokens.txt        - Lexical tokens")
    print("  • symbol_table.txt  - Variable symbols")
    print("  • tac.txt           - Three Address Code (TAC)")
    print("  • opt.txt           - Optimized TAC")
    print("  • parser_output.txt - Parse tree rules")
    print("  • errors.txt        - Compilation errors")
    print("  • assembly.asm      - Assembly code")
    print("="*50)


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
        dup_count = 0
        
        for line in lines[2:]:          # skip header lines
            if line != prev:
                f.write(line)
                prev = line
            else:
                dup_count += 1
    
    if dup_count > 0:
        print(f"    Removed {dup_count} duplicate instructions")


if __name__ == "__main__":
    main()
