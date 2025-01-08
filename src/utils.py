import re


def is_latin_alph(c: str) -> bool:
    return re.fullmatch(r"[a-zA-Z]", c) is not None