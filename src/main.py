import sys
from tokenizer.lexer import Lexer



if __name__ == "__main__":
    lexer = Lexer()
    with open(sys.argv[1]) as f:
        code = f.read()
        tokens = lexer.tokenize(code)
        print(lexer)
        