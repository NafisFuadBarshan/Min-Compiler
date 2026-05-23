import re
from dataclasses import dataclass


# ── Token dataclass ────────────────────────────────────────────────────────────

@dataclass
class Token:
    kind:   str   # e.g. "Keyword", "Identifier", "Number" …
    lexeme: str
    line:   int


# ── Keyword set ────────────────────────────────────────────────────────────────

KEYWORDS = {"int", "if", "else", "while", "print"}


# ── Lexer ─────────────────────────────────────────────────────────────────────

class Lexer:
    """
    Hand-written lexer that produces the same token stream as the
    flex-based lexer.l.
    """

    # Token patterns – order matters (longer matches first for multi-char ops)
    _PATTERNS = [
        ("relop",       r"==|!=|>=|<=|>|<"),
        ("assign",      r"="),
        ("arithmetic",  r"[+\-*/%]"),
        ("punctuation", r";"),
        ("lparen",      r"[({]"),
        ("rparen",      r"[)}]"),
        ("number",      r"\d+"),
        ("ident",       r"[A-Za-z_]\w*"),
        ("whitespace",  r"[ \t\r\n]+"),
        ("unknown",     r"."),
    ]

    _MASTER = re.compile(
        "|".join(f"(?P<{name}>{pat})" for name, pat in _PATTERNS)
    )

    def __init__(self, source: str):
        self._source = source
        self.tokens: list[Token] = []

    # ── public ────────────────────────────────────────────────────────────────

    def tokenize(self) -> list[Token]:
        line = 1
        for m in self._MASTER.finditer(self._source):
            kind = m.lastgroup
            text = m.group()

            if kind == "whitespace":
                line += text.count("\n")
                continue

            tok = self._classify(kind, text, line)
            if tok:
                self.tokens.append(tok)

        return self.tokens

    def write_tokens(self, path: str):
        with open(path, "w") as f:
            f.write("Token Type\tLexeme\n")
            f.write("-------------------------\n")
            for t in self.tokens:
                f.write(f"{t.kind}\t\t{t.lexeme}\n")

    # ── private ───────────────────────────────────────────────────────────────

    @staticmethod
    def _classify(kind: str, text: str, line: int) -> Token | None:
        if kind == "ident":
            if text in KEYWORDS:
                return Token("Keyword", text, line)
            return Token("Identifier", text, line)

        if kind == "number":
            return Token("Number", text, line)

        if kind == "relop":
            return Token("Relop", text, line)

        if kind == "assign":
            return Token("Assignment", text, line)

        if kind == "arithmetic":
            return Token("Arithmetic", text, line)

        if kind == "punctuation":
            return Token("Punctuation", text, line)

        if kind in ("lparen", "rparen"):
            return Token("Parenthesis", text, line)

        if kind == "unknown":
            return Token("Unknown", text, line)

        return None
if __name__ == "__main__":
    with open("input.txt") as f:
        source = f.read()
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    lexer.write_tokens("tokens.txt")
    print(f"Lexing done. {len(tokens)} tokens found.")
    for t in tokens:
        print(f"  {t.kind:<15} {t.lexeme}")