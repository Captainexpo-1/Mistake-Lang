import sys
from tokenizer.lexer import Lexer
from parser.parser import Parser
from runtime.interpreter import Interpreter

if __name__ == "__main__":
    lexer = Lexer()
    parser = Parser()
    runtime = Interpreter()
    
    with open(sys.argv[1]) as f:
        code = f.read()
        
        tokens = lexer.tokenize(code)
        print(lexer)
        
        parser.parse(tokens)
        print(parser.ast)
        
        e = runtime.execute(parser.ast)
        print(e)
        