import sys
import os
from mistake.tokenizer.lexer import Lexer
from mistake.parser.parser import Parser
from mistake.runtime.interpreter import Interpreter
import time

def get_args() -> tuple[str, set]:
    if len(sys.argv) < 2:
        print("Usage: python main.py <file>")
        sys.exit(1)

    return sys.argv[1], set(sys.argv[2:])


def main():
    fname, args = get_args()

    lexer = Lexer()
    parser = Parser()
    runtime = Interpreter("--unsafe" in args)
    p_time = "--time" in args
    with open(fname) as f:
        if p_time: print("Read file:", time.process_time())
        start = time.time()

        os.chdir(os.path.dirname(os.path.abspath(fname)))
        code = f.read()
        
        tokens = lexer.tokenize(code)
        if p_time: print("Tokenized:", time.process_time())
        
        if "-tokens" in args:
            print(tokens)
            
        ast = parser.parse(tokens)
        if p_time: print("Parsed:", time.process_time())
        if "-ast" in args:
            print(ast)
        if "-e" in args:
            runtime.execute(ast, filename=fname)
            
        if p_time: print(f"Total runtime: {time.time() - start} seconds")
if __name__ == "__main__":
    main()
