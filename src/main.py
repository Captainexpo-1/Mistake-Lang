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
        #print(lexer)
        
        #print("\n---------- ast ----------")
        ast = parser.parse(tokens)
       # print(ast)
        
        if "-e" in args:
            e = runtime.execute(ast)
            #print(e)
        