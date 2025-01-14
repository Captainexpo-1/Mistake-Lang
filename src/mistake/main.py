import sys
import os
from mistake.tokenizer.lexer import Lexer
from mistake.parser.parser import Parser
from mistake.runtime.interpreter import Interpreter
import time
from typing import Tuple, List
from dotenv import load_dotenv

ENV_PATH = None

def get_args() -> Tuple[str, List[str]]:
    if len(sys.argv) < 2:
        print("Usage: python main.py <file>")
        sys.exit(1)

    return sys.argv[1], sys.argv[2:]

def main():
    global ENV_PATH
    fname, args = get_args()
    p_time = "--time" in args

    lexer = Lexer()
    parser = Parser()
    runtime = Interpreter("--unsafe" in args)

    get_env =  args.index("--env") if "--env" in args else -1
    ENV_PATH = None if get_env == -1 else args[get_env + 1] 
    if ENV_PATH is not None: load_dotenv(ENV_PATH)
    else: load_dotenv()
    
    with open(fname, "r", encoding='utf-8') as f:
        if p_time:
            print("Read file:", time.process_time())
        start = time.time()

        os.chdir(os.path.dirname(os.path.abspath(fname)))
        code = f.read()

        tokens = lexer.tokenize(code)
        if p_time:
            print("Tokenized:", time.process_time())

        if "--tokens" in args:
            print(tokens)

        ast = parser.parse(tokens)
        if p_time:
            print("Parsed:", time.process_time())

        if "--ast" in args:
            open("ast.txt", "w").write(str(ast))
            print(ast)

        if "--no-exe" not in args:
            runtime.execute(ast, filename=fname)

        if p_time:
            print(f"Total runtime: {time.time() - start} seconds")


if __name__ == "__main__":
    main()
