import sys
from tokenizer.lexer import Lexer
from parser.parser import Parser
from typing import List

def fetch_file(filename: str) -> List:
    lexer = Lexer()
    parser = Parser()
    with open(filename) as f:
        code = f.read()
        tokens = lexer.tokenize(code)
        ast = parser.parse(tokens)
        return ast
    