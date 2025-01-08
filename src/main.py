import sys
from tokenizer.lexer import Lexer
from parser.parser import Parser
from runtime.interpreter import Interpreter

def get_args() -> tuple[str, set]:
    if len(sys.argv) < 2:
        print("Usage: python main.py <file>")
        sys.exit(1)

    return sys.argv[1], set(sys.argv[2:])




if __name__ == "__main__":
    fname, args = get_args()
    
    lexer = Lexer()
    parser = Parser()
    runtime = Interpreter()
    
    with open(fname) as f:
        code = f.read()
        tokens = lexer.tokenize(code)
        if "-tokens" in args: print(tokens)
        ast = parser.parse(tokens)
        if "-ast" in args: print(ast)
        if "-e" in args: runtime.execute(ast, filename=fname)
            #print(e)
        