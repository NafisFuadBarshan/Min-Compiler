"""
parser_.py  –  Recursive-descent parser
Mirrors the Bison grammar in parser.y with identical semantic actions:
  • Symbol table management
  • Three-address code (TAC) emission
  • Parser-output log
  • Error collection
"""

from __future__ import annotations
from dataclasses import dataclass, field
from lexer import Token


# ── Symbol table entry ────────────────────────────────────────────────────────

@dataclass
class Symbol:
    name:    str
    type_:   str  = "int"
    size:    int  = 4
    dim:     int  = 0
    line:    int  = 0
    address: int  = 0


# ── Parser ────────────────────────────────────────────────────────────────────

class Parser:
    def __init__(self, tokens: list[Token]):
        self._tokens  = tokens
        self._pos     = 0

        # outputs
        self.symbol_table:  list[Symbol] = []
        self.tac_lines:     list[str]    = []
        self.parse_log:     list[str]    = []
        self.errors:        list[str]    = []

        # counters
        self._temp_count  = 0
        self._label_count = 0
        self._address     = 1000

    # ═══════════════════════════════════════════════════════════════════════════
    # Public interface
    # ═══════════════════════════════════════════════════════════════════════════

    def parse(self):
        self._program()

    def write_symbol_table(self, path: str):
        with open(path, "w") as f:
            f.write("Name\tType\tSize\tDim\tLine\tAddress\n")
            f.write("---------------------------------------------\n")
            for s in self.symbol_table:
                f.write(f"{s.name}\t{s.type_}\t{s.size}\t"
                        f"{s.dim}\t{s.line}\t{s.address}\n")

    def write_tac(self, path: str):
        with open(path, "w") as f:
            f.write("Three Address Code\n")
            f.write("------------------\n")
            for line in self.tac_lines:
                f.write(line + "\n")

    def write_parser_output(self, path: str):
        with open(path, "w") as f:
            f.write("Grammar Rules Matched\n")
            f.write("---------------------\n")
            for line in self.parse_log:
                f.write(line + "\n")

    def write_errors(self, path: str):
        with open(path, "w") as f:
            f.write("Error List\n")
            f.write("----------\n")
            for e in self.errors:
                f.write(e + "\n")

    # ═══════════════════════════════════════════════════════════════════════════
    # Helpers
    # ═══════════════════════════════════════════════════════════════════════════

    def _peek(self) -> Token | None:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None

    def _current_line(self) -> int:
        t = self._peek()
        return t.line if t else 0

    def _match(self, kind: str, lexeme: str | None = None) -> Token | None:
        t = self._peek()
        if t is None:
            return None
        kind_ok   = (t.kind == kind)
        lexeme_ok = (lexeme is None or t.lexeme == lexeme)
        if kind_ok and lexeme_ok:
            self._pos += 1
            return t
        return None

    def _expect(self, kind: str, lexeme: str | None = None) -> Token:
        t = self._match(kind, lexeme)
        if t is None:
            got  = self._peek()
            desc = f"{got.kind}('{got.lexeme}')" if got else "EOF"
            msg  = (f"Syntax Error line {self._current_line()}: "
                    f"expected {kind}"
                    + (f"('{lexeme}')" if lexeme else "")
                    + f" got {desc}")
            self.errors.append(msg)
            # panic recovery: skip one token
            if self._pos < len(self._tokens):
                self._pos += 1
            # return a dummy token so callers don't crash
            return Token(kind, lexeme or "", self._current_line())
        return t

    # ── TAC / label helpers ───────────────────────────────────────────────────

    def _new_temp(self) -> str:
        t = f"t{self._temp_count}"
        self._temp_count += 1
        return t

    def _new_label(self) -> str:
        l = f"L{self._label_count}"
        self._label_count += 1
        return l

    def _emit(self, line: str):
        self.tac_lines.append(line)

    def _log(self, rule: str):
        self.parse_log.append(rule)

    # ── Symbol table ──────────────────────────────────────────────────────────

    def _exists(self, name: str) -> bool:
        return any(s.name == name for s in self.symbol_table)

    def _add_symbol(self, name: str, line: int):
        if not self._exists(name):
            sym = Symbol(name=name, line=line, address=self._address)
            self.symbol_table.append(sym)
            self._address += 4
        else:
            self.errors.append(
                f"Semantic Error line {line}: {name} redeclared")

    def _check_declared(self, name: str, line: int):
        if not self._exists(name):
            self.errors.append(
                f"Semantic Error line {line}: {name} not declared")

    @staticmethod
    def _is_number(s: str) -> bool:
        return s.lstrip("-").isdigit()

    # ═══════════════════════════════════════════════════════════════════════════
    # Grammar rules  (mirrors parser.y top-down)
    # ═══════════════════════════════════════════════════════════════════════════

    def _program(self):
        self._statements()
        self._log("program -> statements")

    # ── statements ────────────────────────────────────────────────────────────

    def _statements(self):
        """statements : statement | statements statement"""
        first = True
        while self._peek() is not None:
            before = self._pos
            self._statement()
            if self._pos == before:       # nothing consumed → stop
                break
            if first:
                self._log("statements -> statement")
                first = False
            else:
                self._log("statements -> statements statement")

    def _statement(self):
        t = self._peek()
        if t is None:
            return

        if t.kind == "Keyword" and t.lexeme == "int":
            self._declaration()
            self._log("statement -> declaration")

        elif t.kind == "Keyword" and t.lexeme == "if":
            self._if_stmt()
            self._log("statement -> if_stmt")

        elif t.kind == "Keyword" and t.lexeme == "while":
            self._while_stmt()
            self._log("statement -> while_stmt")

        elif t.kind == "Keyword" and t.lexeme == "print":
            self._print_stmt()
            self._log("statement -> print_stmt")

        elif t.kind == "Identifier":
            self._assignment()
            self._log("statement -> assignment")

        # else: unknown token – leave it for the caller

    # ── declaration ───────────────────────────────────────────────────────────

    def _declaration(self):
        line = self._current_line()
        self._expect("Keyword", "int")
        id_tok = self._expect("Identifier")
        name   = id_tok.lexeme

        if self._match("Assignment", "="):
            expr = self._expression()
            self._expect("Punctuation", ";")
            self._add_symbol(name, line)
            self._emit(f"{name} = {expr}")
            self._log(f"declaration -> int id = expression ;")
        else:
            self._expect("Punctuation", ";")
            self._add_symbol(name, line)
            self._log("declaration -> int id ;")

    # ── assignment ────────────────────────────────────────────────────────────

    def _assignment(self):
        line   = self._current_line()
        id_tok = self._expect("Identifier")
        name   = id_tok.lexeme
        self._expect("Assignment", "=")
        expr = self._expression()
        self._expect("Punctuation", ";")
        self._check_declared(name, line)
        self._emit(f"{name} = {expr}")
        self._log("assignment -> id = expression ;")

    # ── print ─────────────────────────────────────────────────────────────────

    def _print_stmt(self):
        self._expect("Keyword", "print")
        self._expect("Parenthesis", "(")
        expr = self._expression()
        self._expect("Parenthesis", ")")
        self._expect("Punctuation", ";")
        self._emit(f"PRINT {expr}")
        self._log("print_stmt -> print ( expression ) ;")

    # ── if / else ─────────────────────────────────────────────────────────────

    def _if_stmt(self):
        self._expect("Keyword", "if")
        self._expect("Parenthesis", "(")
        cond = self._condition()
        self._expect("Parenthesis", ")")

        false_lbl = self._new_label()
        end_lbl   = self._new_label()
        self._emit(f"IF_FALSE {cond} GOTO {false_lbl}")

        self._expect("Parenthesis", "{")
        self._statements()
        self._expect("Parenthesis", "}")

        # else_part
        if self._match("Keyword", "else"):
            self._emit(f"GOTO {end_lbl}")
            self._emit(f"LABEL {false_lbl}")
            self._expect("Parenthesis", "{")
            self._statements()
            self._expect("Parenthesis", "}")
            self._emit(f"LABEL {end_lbl}")
            self._log("else_part -> else { statements }")
        else:
            self._emit(f"LABEL {false_lbl}")
            self._log("else_part -> empty")

        self._log("if_stmt -> if ( condition ) { statements } else_part")

    # ── while ─────────────────────────────────────────────────────────────────

    def _while_stmt(self):
        self._expect("Keyword", "while")
        start_lbl = self._new_label()
        end_lbl   = self._new_label()
        self._emit(f"LABEL {start_lbl}")

        self._expect("Parenthesis", "(")
        cond = self._condition()
        self._expect("Parenthesis", ")")
        self._emit(f"IF_FALSE {cond} GOTO {end_lbl}")

        self._expect("Parenthesis", "{")
        self._statements()
        self._expect("Parenthesis", "}")

        self._emit(f"GOTO {start_lbl}")
        self._emit(f"LABEL {end_lbl}")
        self._log("while_stmt -> while ( condition ) { statements }")

    # ── condition ─────────────────────────────────────────────────────────────

    def _condition(self) -> str:
        left  = self._expression()
        op    = self._relop()
        right = self._expression()

        if self._is_number(left) and self._is_number(right):
            a, b = int(left), int(right)
            result = {
                ">": a > b, "<": a < b, ">=": a >= b,
                "<=": a <= b, "==": a == b, "!=": a != b,
            }.get(op, False)
            t = self._new_temp()
            self.tac_lines  # no TAC for constant folded
            self._log("condition -> expression relop expression")
            return str(int(result))

        t = self._new_temp()
        self._emit(f"{t} = {left} {op} {right}")
        self._log("condition -> expression relop expression")
        return t

    def _relop(self) -> str:
        t = self._peek()
        if t and t.kind == "Relop":
            self._pos += 1
            return t.lexeme
        self.errors.append(
            f"Syntax Error line {self._current_line()}: expected relop")
        return "?"

    # ── expression ────────────────────────────────────────────────────────────

    def _expression(self) -> str:
        left = self._term()
        self._log("expression -> term")

        while True:
            t = self._peek()
            if t is None or t.kind != "Arithmetic" or t.lexeme not in ("+", "-"):
                break
            op = t.lexeme
            self._pos += 1
            right = self._term()

            if self._is_number(left) and self._is_number(right):
                val  = int(left) + int(right) if op == "+" else int(left) - int(right)
                left = str(val)
            else:
                tmp = self._new_temp()
                self._emit(f"{tmp} = {left} {op} {right}")
                left = tmp
            self._log(f"expression -> expression {op} term")

        return left

    # ── term ──────────────────────────────────────────────────────────────────

    def _term(self) -> str:
        left = self._factor()
        self._log("term -> factor")

        while True:
            t = self._peek()
            if t is None or t.kind != "Arithmetic" or t.lexeme not in ("*", "/"):
                break
            op = t.lexeme
            self._pos += 1
            right = self._factor()

            if self._is_number(left) and self._is_number(right):
                val  = int(left) * int(right) if op == "*" else int(left) // int(right)
                left = str(val)
            else:
                tmp = self._new_temp()
                self._emit(f"{tmp} = {left} {op} {right}")
                left = tmp
            self._log(f"term -> term {op} factor")

        return left

    # ── factor ────────────────────────────────────────────────────────────────

    def _factor(self) -> str:
        t = self._peek()
        if t is None:
            self.errors.append("Syntax Error: unexpected end of input in factor")
            return "0"

        if t.kind == "Identifier":
            self._pos += 1
            self._check_declared(t.lexeme, t.line)
            self._log("factor -> id")
            return t.lexeme

        if t.kind == "Number":
            self._pos += 1
            self._log("factor -> number")
            return t.lexeme

        if t.kind == "Parenthesis" and t.lexeme == "(":
            self._pos += 1
            val = self._expression()
            self._expect("Parenthesis", ")")
            self._log("factor -> ( expression )")
            return val

        self.errors.append(
            f"Syntax Error line {t.line}: unexpected token '{t.lexeme}' in factor")
        self._pos += 1
        return "0"
