from parser import parser
from parser.ast import *
from tokenizer.lexer import Lexer


def do_test(src: str, expected: List[ASTNode]):
    l = Lexer()
    p = parser.Parser()
    tokens = l.tokenize(src)
    parsed = p.parse(tokens)
    print(parsed, expected)
    assert str(parsed) == str(expected)
def test_parser():
    do_test("variable $1 is 1 end", [VariableDeclaration("$1", Number(1))])
    do_test("!? 1 end", [FunctionApplication(VariableAccess("!?"), Number(1))])
    do_test("variable $1 is 1 end \n variable $2 is + 1 $1 end", expected=[
        VariableDeclaration("$1", Number(1)), 
        VariableDeclaration("$2", 
            FunctionApplication(
                FunctionApplication(
                    VariableAccess('+'),
                    Number(1)
                ),
                VariableAccess('$1')
            )
        )
    ])
    do_test("+ 3 + 4 5 end", expected=[
        FunctionApplication(
            FunctionApplication(
                VariableAccess('+'),
                Number(3)
            ),
            FunctionApplication(
                FunctionApplication(
                    VariableAccess('+'),
                    Number(4),
                ),
                Number(5)
            )
        )
    ])
    
if __name__ == "__main__":
    test_parser()
    print("All tests passed!")