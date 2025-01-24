from enum import Enum
from typing import Any


class TokenType(Enum):
    ERROR = -1
    KW_VARIABLE = 0
    KW_IS = 1
    KW_OPEN = 2
    KW_CLOSE = 3
    KW_IMPURE = 9

    SYM_IDENTIFIER = 11
    KW_STRING = 12

    SYM_OPEN_PAREN = 14
    SYM_CLOSE_PAREN = 15
    KW_END = 16
    KW_RETURNS = 17

    SYM_WHITESPACE = 19
    SYM_DURATION = 20
    KW_LIFETIME = 21

    KW_PUBLIC = 24
    KW_RANDOMIZE = 25
    KW_TYPE = 26

    # TYPES
    TYPE_NUMBER = 27
    TYPE_BOOLEAN = 29

    # LITERALS
    KW_UNIT = 31
    KW_TRUE = 22
    KW_FALSE = 23
    KW_FUNCTION = 10
    SYM_STRING = 18
    SYM_NUMBER = 13

    KW_JUMP = 30
    KW_NEW = 32
    KW_CLASS = 33
    KW_INHERITS = 34
    KW_HAS = 35
    KW_MATCH = 36
    KW_CASES = 38
    KW_CASE = 37
    KW_OTHERWISE = 39
    KW_MEMBER = 40
    KW_THEN = 41
    KW_OF = 42
    KW_DO = 43
    KW_USE = 44
    KW_FROM = 45
    KW_WITH = 46
    
    EX_COMMENT = 47
    EX_STRING = 48
    
    SYM_EOF = 100


opening_tokens = [
    TokenType.KW_OPEN,
    TokenType.KW_CASES,
    TokenType.KW_CASE,
    TokenType.KW_OTHERWISE,
    TokenType.KW_RETURNS,
    TokenType.KW_HAS,
    TokenType.SYM_STRING,
]


class Token:
    def __init__(self, type: TokenType, value: Any, line: int = 0):
        self.value = value
        self.type = type
        self.line = line

    def __str__(self) -> str:
        v = self.value
        v = v.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
        return f'Token({self.type}: "{v}")'

    def __repr__(self) -> str:
        return str(self)
