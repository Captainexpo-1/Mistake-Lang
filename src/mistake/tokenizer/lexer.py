from mistake.tokenizer.token import *
from mistake.utils import *
from typing import List
from mistake.parser.errors.parser_errors import *
import re
import html

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
        "string": TokenType.KW_STRING,
        "lifetime": TokenType.KW_LIFETIME,
        "true": TokenType.KW_TRUE,
        "false": TokenType.KW_FALSE,
        "public": TokenType.KW_PUBLIC,
        "randomize": TokenType.KW_RANDOMIZE,
        "type": TokenType.KW_TYPE,
        "number": TokenType.TYPE_NUMBER,
        "boolean": TokenType.TYPE_BOOLEAN,
        "unit": TokenType.KW_UNIT,
        "jump": TokenType.KW_JUMP,
        "new": TokenType.KW_NEW,
        "class": TokenType.KW_CLASS,
        "inherits": TokenType.KW_INHERITS,
        "has": TokenType.KW_HAS,
        "match": TokenType.KW_MATCH,
        "case": TokenType.KW_CASE,
        "cases": TokenType.KW_CASES,
        "otherwise": TokenType.KW_OTHERWISE,
        "member": TokenType.KW_MEMBER,
        "then": TokenType.KW_THEN,
        "of": TokenType.KW_OF
    }

    def __init__(self):
        self.errors: List[ParserError] = []
        self.tokens: List[Token] = []
        self.code = ""
        self.current_token = None
        self.current_position = 0
        self.current_line = 1

    def add_token(self, token: Token):
        self.tokens.append(token)

    def is_identifier(self, s: str) -> bool:
        contains_non_number = False
        for c in s:
            if not c.isdigit(): contains_non_number = True
            if is_latin_alph(c): return False
        return contains_non_number
            
    def get_token(self, s: str) -> TokenType:
        if re.fullmatch(r"\-?[0-9]+(\.[0-9]+)?", s) != None: 
            return TokenType.SYM_NUMBER
        if s[:-1].isdigit() and s[-1] in 'lust':
            return TokenType.SYM_DURATION
        if self.is_identifier(s):
            return TokenType.SYM_IDENTIFIER
        
        return Lexer.keywords.get(s, TokenType.ERROR)

    def skip_whitespace(self):
        while self.current_position < len(self.code) and self.code[self.current_position].isspace():
            if self.code[self.current_position] == '\n':
                self.current_line += 1
            self.current_position += 1
    
    def skip_line(self):
        while self.current_position < len(self.code) and self.code[self.current_position] != '\n':
            self.current_position += 1
        self.current_line += 1
        self.current_position += 1
    
    def get_string(self) -> str:
        start = self.current_position
        while self.current_position < len(self.code) and self.code[self.current_position:self.current_position+5] != "close":
            self.current_position += 1
            
        return html.unescape(self.code[start+1:self.current_position-1])
    
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
                self.add_token(Token(TokenType.SYM_STRING, self.get_string(), self.current_line))
                continue
            
            token_type = self.get_token(t)
            if token_type == TokenType.ERROR:
                self.add_token(Token(TokenType.ERROR, t, self.current_line))
            else:
                self.add_token(Token(token_type, t, self.current_line))
        
        self.add_token(Token(TokenType.SYM_EOF, "EOF", self.current_line))
        return self.tokens
    
    def __str__(self):
        return "\n".join([str(token) for token in self.tokens])
    
    def __repr__(self):
        return self.__str__()