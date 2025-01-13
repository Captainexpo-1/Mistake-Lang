import re


def is_latin_alph(c: str) -> bool:
    return re.fullmatch(r"[a-zA-Z]", c) is not None


def to_decimal_seconds(seconds: float):
    return seconds * 0.864


def from_decimal_seconds(seconds: float):
    return seconds / 0.864

