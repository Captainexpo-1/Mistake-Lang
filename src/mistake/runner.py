from mistake.parser.parser import Parser
from mistake.tokenizer.lexer import Lexer
from mistake.tokenizer.token import Token
from mistake.runtime.interpreter import Interpreter
from mistake.runtime.runtime_types import MLType
from typing import List

def fetch_file(filename: str) -> List[Token]:
    return Parser().parse(Lexer().tokenize(open(filename).read()))

def run_script(program: str, lex=Lexer(),parser=Parser(),rt=Interpreter(),standalone=True) -> List[MLType]:
    tokens: List[Token] = lex.tokenize(program)
    ast = parser.parse(tokens)
    return rt.execute(ast, standalone=standalone)