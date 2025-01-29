from mistake.parser.parser import Parser
from mistake.tokenizer.lexer import Lexer
from typing import List

def fetch_file(filename: str) -> List:
    return Parser().parse(Lexer().tokenize(open(filename).read()))
