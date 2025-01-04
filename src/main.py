import sys
from tokenizer.lexer import Lexer
from parser.parser import Parser


if __name__ == "__main__":
    lexer = Lexer()
    parser = Parser()
    with open(sys.argv[1]) as f:
        code = f.read()
        tokens = lexer.tokenize(code)
        print(lexer)
        parser.parse(tokens)
        print(parser.ast)
        
        