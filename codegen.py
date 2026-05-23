from __future__ import annotations
import re


class CodeGen:
    def __init__(self, tac_lines: list[str], symbol_table):
        self._tac    = tac_lines
        self._symtab = symbol_table
        self._asm: list[str] = []
        self._temps: set[str] = set()  # Track temporary variables

    # ── public ────────────────────────────────────────────────────────────────

    def generate(self):
        self._asm.append("Assembly Code")
        self._asm.append("-------------")

        # First pass: collect all temporary variables used in TAC
        self._collect_temps()

        for line in self._tac:
            line = line.strip()
            if not line:
                continue

            # LABEL X
            m = re.fullmatch(r"LABEL (\S+)", line)
            if m:
                self._asm.append(f"{m.group(1)}:")
                continue

            # PRINT x
            m = re.fullmatch(r"PRINT (\S+)", line)
            if m:
                self._asm.append(f"PRINT {m.group(1)}")
                continue

            # IF_FALSE t GOTO L
            m = re.fullmatch(r"IF_FALSE (\S+) GOTO (\S+)", line)
            if m:
                cond, lbl = m.group(1), m.group(2)
                self._asm.append(f"CMP {cond}, 0")
                self._asm.append(f"JE {lbl}")
                continue

            # GOTO L
            m = re.fullmatch(r"GOTO (\S+)", line)
            if m:
                self._asm.append(f"JMP {m.group(1)}")
                continue

            # DECLARE x  (not emitted in TAC but handle if present)
            m = re.fullmatch(r"DECLARE (\S+)", line)
            if m:
                self._asm.append(f"DECLARE {m.group(1)}")
                continue

            # t = a op b
            m = re.fullmatch(r"(\S+) = (\S+) ([+\-*/%><!=]+) (\S+)", line)
            if m:
                dst, a, op, b = m.groups()
                self._emit_binop(dst, a, op, b)
                continue

            # dst = src  (simple copy / constant load)
            m = re.fullmatch(r"(\S+) = (\S+)", line)
            if m:
                dst, src = m.group(1), m.group(2)
                self._emit_mov(dst, src)
                continue

        # emit DECLARE for every symbol in the table (mirrors C compiler)
        decl_lines: list[str] = []
        for sym in self._symtab:
            decl_lines.append(f"DECLARE {sym.name}")
        # emit DECLARE for temporary variables
        for temp in sorted(self._temps):
            decl_lines.append(f"DECLARE {temp}")
        # insert declarations right after header
        self._asm[2:2] = decl_lines

    def write(self, path: str):
        with open(path, "w") as f:
            for line in self._asm:
                f.write(line + "\n")

    # ── private ───────────────────────────────────────────────────────────────

    def _collect_temps(self):
        """First pass: identify all temporary variables used in the TAC."""
        for line in self._tac:
            line = line.strip()
            if not line:
                continue
            # Match pattern: t = ... or use of t in expressions
            m = re.fullmatch(r"(\S+) = (\S+) ([+\-*/%><!=]+) (\S+)", line)
            if m:
                self._temps.add(m.group(1))
                # Check if operands are temps
                if m.group(2).startswith('t'):
                    self._temps.add(m.group(2))
                if m.group(4).startswith('t'):
                    self._temps.add(m.group(4))
            
            m = re.fullmatch(r"(\S+) = (\S+)", line)
            if m:
                dst, src = m.group(1), m.group(2)
                if dst.startswith('t'):
                    self._temps.add(dst)
                if src.startswith('t'):
                    self._temps.add(src)
            
            # Check for IF_FALSE and CMP operations
            m = re.fullmatch(r"IF_FALSE (\S+) GOTO (\S+)", line)
            if m and m.group(1).startswith('t'):
                self._temps.add(m.group(1))

    def _is_number(self, s: str) -> bool:
        return s.lstrip("-").isdigit()

    def _emit_mov(self, dst: str, src: str):
        if self._is_number(src):
            # Load immediate directly — no need for a round-trip through R0
            self._asm.append(f"MOV {dst}, {src}")
        else:
            self._asm.append(f"MOV R0, {src}")
            self._asm.append(f"MOV {dst}, R0")

    def _emit_binop(self, dst: str, a: str, op: str, b: str):
        arith_map = {"+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV", "%": "MOD"}
        relop_map = {
            ">":  "SETGT", "<":  "SETLT",
            ">=": "SETGE", "<=": "SETLE",
            "==": "SETE",  "!=": "SETNE",
        }

        if op in arith_map:
            self._asm.append(f"MOV R0, {a}")
            self._asm.append(f"{arith_map[op]} R0, {b}")
            self._asm.append(f"MOV {dst}, R0")

        elif op in relop_map:
            self._asm.append(f"CMP {a}, {b}")
            self._asm.append(f"{relop_map[op]} {dst}")

        else:
            self._asm.append(f"; unknown op: {dst} = {a} {op} {b}")


if __name__ == "__main__":
    from lexer import Lexer
    from parser_ import Parser

    with open("input.txt") as f:
        source = f.read()
    tokens = Lexer(source).tokenize()
    parser = Parser(tokens)
    parser.parse()

    cg = CodeGen(parser.tac_lines, parser.symbol_table)
    cg.generate()
    cg.write("assembly.asm")
    print("Code generation done. Check assembly.asm")
