from mistake.parser import parser
from mistake.parser.ast import *

from mistake.tokenizer.lexer import Lexer


def do_test(src: str, expected: List[ASTNode]):
    l = Lexer()
    p = parser.Parser()
    tokens = l.tokenize(src)
    parsed = p.parse(tokens)
    print(f"{parsed}\n ==\n{expected}\n")
    assert str(parsed) == str(expected)


def test_parser():
    do_test(
        "+ 1 2 end",
        [
            FunctionApplication(
                FunctionApplication(VariableAccess("+"), Number(1)), Number(2)
            )
        ],
    )
    do_test(
        "open = $2 11 close end",
        [
            Block(
                [
                    FunctionApplication(
                        FunctionApplication(VariableAccess("="), VariableAccess("$2")),
                        Number(11),
                    )
                ]
            )
        ],
    )
    do_test("variable $1 is 1 end", [VariableDeclaration("$1", Number(1))])
    do_test("!? 1 end", [FunctionApplication(VariableAccess("!?"), Number(1))])
    do_test(
        "variable $1 is 1 end \n variable $2 is + 1 $1 end",
        expected=[
            VariableDeclaration("$1", Number(1)),
            VariableDeclaration(
                "$2",
                FunctionApplication(
                    FunctionApplication(VariableAccess("+"), Number(1)),
                    VariableAccess("$1"),
                ),
            ),
        ],
    )
    do_test(
        """
            open
                variable $1 is 1 end
                $1
            close end""",
        [Block([VariableDeclaration("$1", Number(1)), VariableAccess("$1")])],
    )
    do_test(
        "variable $5 type number lifetime 20s is 3 end",
        [VariableDeclaration("$5", Number(3), lifetime="20s")],
    )


if __name__ == "__main__":
    test_parser()
    print("All tests passed!")
