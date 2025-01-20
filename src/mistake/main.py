import time
import sys
import os
from mistake.tokenizer.lexer import Lexer
from mistake.parser.parser import Parser
from mistake.runtime.interpreter import Interpreter
from typing import Tuple, List
from dotenv import load_dotenv
import argparse

ENV_PATH = None

def print_help():
    print("Usage: mistake-lang <filename> [--time] [--tokens] [--ast] [--no-exe] [--env <path>] [--vulkan]")

def get_args() -> Tuple[str, List[str]]:
    parser = argparse.ArgumentParser(description='MistakeLang Interpreter')
    parser.add_argument('filename', type=str, help='The script file to run')
    parser.add_argument('--time', action='store_true', help='Print timing information')
    parser.add_argument('--tokens', action='store_true', help='Print tokens')
    parser.add_argument('--ast', action='store_true', help='Print AST')
    parser.add_argument('--no-exe', action='store_true', help='Do not execute the script')
    parser.add_argument('--env', type=str, help='Path to the .env file')
    parser.add_argument('--vulkan', action='store_true', help='Enable Vulkan support')
    parser.add_argument('--unsafe', action='store_true', help='Enable unsafe mode')
    parser.add_argument('--end-env', action='store_true', help='Print the global environment at the end')

    args = parser.parse_args()

    if not os.path.isfile(args.filename):
        print(f"File '{args.filename}' not found")
        sys.exit(1)

    return args

def run_script(program: str, lex=Lexer(), parser=Parser(), rt=Interpreter(), standalone=True) -> List:
    tokens = lex.tokenize(program)
    ast = parser.parse(tokens)
    return rt.execute(ast, standalone=standalone)

def main():
    global ENV_PATH
    args = get_args()
    p_time = args.time

    lexer = Lexer()
    parser = Parser()
    runtime = Interpreter(args.unsafe)

    ENV_PATH = args.env
    if ENV_PATH is not None: 
        load_dotenv(ENV_PATH)
    else: 
        load_dotenv()
    
    with open(args.filename, "r", encoding='utf-8') as f:
        if p_time:
            print("Read file:", time.process_time())
        start = time.time()

        os.chdir(os.path.dirname(os.path.abspath(args.filename)))
        code = f.read()

        tokens = lexer.tokenize(code)
        if p_time:
            print("Tokenized:", time.process_time())

        if args.tokens:
            print(tokens)

        ast = parser.parse(tokens)
        if p_time:
            print("Parsed:", time.process_time())

        if args.ast:
            open("ast.txt", "w").write(str(ast))
            print(ast)

        if not args.no_exe:
            runtime.execute(ast, filename=args.filename)
        
        if args.end_env:
            print(runtime.global_environment)
        
        if p_time:
            print(f"Total runtime: {time.time() - start} seconds")

if __name__ == "__main__":
    main()
