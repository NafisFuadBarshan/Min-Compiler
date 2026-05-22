"""
codegen.py  –  Assembly code generator
Converts TAC lines → pseudo-assembly that mirrors assembly.asm.
"""

from __future__ import annotations
import re


class CodeGen:
    def __init__(self, tac_lines: list[str], symbol_table):
        self._tac    = tac_lines
        self._symtab = symbol_table
        self._asm: list[str] = []

    # ── public ────────────────────────────────────────────────────────────────

    def generate(self):
        self._asm.append("Assembly Code")
        self._asm.append("-------------")

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
            m = re.fullmatch(r"(\S+) = (\S+) ([+\-*/><!=]+) (\S+)", line)
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
        # insert declarations right after header
        self._asm[2:2] = decl_lines

    def write(self, path: str):
        with open(path, "w") as f:
            for line in self._asm:
                f.write(line + "\n")

    # ── private ───────────────────────────────────────────────────────────────

    def _is_number(self, s: str) -> bool:
        return s.lstrip("-").isdigit()

    def _emit_mov(self, dst: str, src: str):
        if self._is_number(src):
            self._asm.append(f"MOV R0, {src}")
            self._asm.append(f"MOV {dst}, R0")
        else:
            self._asm.append(f"MOV R0, {src}")
            self._asm.append(f"MOV {dst}, R0")

    def _emit_binop(self, dst: str, a: str, op: str, b: str):
        arith_map = {"+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV"}
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
