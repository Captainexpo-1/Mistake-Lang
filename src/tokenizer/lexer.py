from tokenizer.token import *
from utils import *
from typing import List

class Lexer:
    keywords: dict[str, TokenType] = {
        "variable": TokenType.KW_VARIABLE,
        "is": TokenType.KW_IS,
        "open": TokenType.KW_OPEN,
        "close": TokenType.KW_CLOSE,
        "impure": TokenType.KW_IMPURE,
        "function": TokenType.KW_FUNCTION,
        "end": TokenType.KW_END,
        "returns": TokenType.KW_RETURNS,
        "string": TokenType.KW_STRING
    }

    def __init__(self):
        self.tokens = []
        self.code = ""
        self.current_token = None
        self.current_position = 0
        self.current_line = 1

    def is_identifier(self, s: str) -> bool:
        contains_non_number = False
        for c in s:
            if not c.isdigit(): contains_non_number = True
            if is_latin_alph(c): return False
        return contains_non_number
            
    def get_token(self, s: str) -> TokenType:
        if s.isdigit(): return TokenType.SYM_NUMBER
        if self.is_identifier(s):
            return TokenType.SYM_IDENTIFIER
        
        return Lexer.keywords.get(s, TokenType.ERROR)

    def skip_whitespace(self):
        while self.current_position < len(self.code) and self.code[self.current_position].isspace():
            if self.code[self.current_position] == '\n':
                self.current_line += 1
                self.tokens.append(Token(TokenType.SYM_NEWLINE, "NL", self.current_line))
            self.current_position += 1
    
    def skip_line(self):
        while self.current_position < len(self.code) and self.code[self.current_position] != '\n':
            self.current_position += 1
        self.current_line += 1
        self.current_position += 1
        self.tokens.append(Token(TokenType.SYM_NEWLINE, "NL", self.current_line))
    
    def get_string(self) -> str:
        start = self.current_position
        while self.current_position < len(self.code) and self.code[self.current_position:self.current_position+5] != "close":
            self.current_position += 1
        return self.code[start:self.current_position]
    
    def tokenize(self, code: str) -> List[Token]:
        self.code = code
        while self.current_position < len(self.code):
            self.skip_whitespace()
            if self.current_position >= len(self.code): break

            start = self.current_position
            while self.current_position < len(self.code) and not self.code[self.current_position].isspace():
                self.current_position += 1

            t = self.code[start:self.current_position]
                
            if t == "comment":
                self.skip_line()
                continue
            
            if t == "string":
                self.tokens.append(Token(TokenType.SYM_STRING, self.get_string(), self.current_line))
                continue
            
            token_type = self.get_token(t)
            if token_type == TokenType.ERROR:
                raise Exception(f"Unknown token '{t}' at line {self.current_line}")
            self.tokens.append(Token(token_type, t, self.current_line))
        
        return self.tokens
    
    def __str__(self):
        return "\n".join([str(token) for token in self.tokens])
    
    def __repr__(self):
        return self.__str__()

            
        
    