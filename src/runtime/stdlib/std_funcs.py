from runtime.errors.runtime_errors import *
from runtime.runtime_types import *
import runtime.interpreter as runtime
import runtime.environment as environment
""" 
format:
! = bang
? = qmark
[ = lbrack
] = rbrack
{ = lbrace
} = rbrace
( = lparen
) = rparen
"""

def fn_bang_qmark(arg: MLType, env: 'environment.Environment', ctx: dict[str, any], interpreter: 'runtime.Interpreter'):
    print(arg)

std_funcs = {
    '!?': BuiltinFunction(fn_bang_qmark),
    '+': BuiltinFunction(lambda x, *_: BuiltinFunction(lambda y: Number(x.value + y.value))),
}