from enum import Enum


class TokenType(Enum):
    ERROR = -1
    KW_VARIABLE = 0
    KW_IS = 1
    KW_OPEN = 2
    KW_CLOSE = 3
    KW_IMPURE = 9
    KW_FUNCTION = 10
    SYM_IDENTIFIER = 11
    KW_STRING = 12
    SYM_NUMBER = 13
    SYM_OPEN_PAREN = 14
    SYM_CLOSE_PAREN = 15
    KW_END = 16
    KW_RETURNS = 17
    SYM_STRING = 18
    SYM_NEWLINE = 19
    SYM_DURATION = 20
    KW_LIFETIME = 21
    KW_TRUE = 22
    KW_FALSE = 23
    KW_PUBLIC = 24
    KW_RANDOMIZE = 25
    KW_TYPE = 26
    
    # TYPES
    TYPE_NUMBER = 27
    TYPE_STRING = 28
    TYPE_BOOLEAN = 29
    TYPE_FUNCTION = 30
    TYPE_UNIT = 31
    
    SYM_EOF = 100

class Token:
    def __init__(self, type: TokenType, value: any, line: int = 0):
        self.value = value
        self.type = type
        self.line = line
    
    def __str__(self) -> str: return f"Token({self.type}: \"{self.value}\")"
    def __repr__(self) -> str: return str(self)