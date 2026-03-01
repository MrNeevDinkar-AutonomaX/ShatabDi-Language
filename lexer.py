import re

TOKEN_SPEC = [
    ("NUMBER", r"\d+"),
    ("ID", r"[a-zA-Z_]\w*"),
    ("OP", r"[+\-*/=><]"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("COMMA", r","),
    ("STRING", r'"[^"]*"'),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
]

def tokenize(code):
    tok_regex = "|".join(f"(?P<{name}>{regex})" for name, regex in TOKEN_SPEC)
    for match in re.finditer(tok_regex, code):
        kind = match.lastgroup
        value = match.group()
        if kind == "SKIP":
            continue
        yield (kind, value)