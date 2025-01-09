from runtime.errors.runtime_errors import *
from runtime.runtime_types import *
import runtime.environment as environment
import runtime.interpreter as interpreter
from parser.ast import *
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

def fn_bang_qmark(arg: MLType, *_):
    print(arg)

def get_type(val: any):
    if isinstance(val, bool):
        return RuntimeBoolean(val)
    if isinstance(val, int) or isinstance(val, float):
        return RuntimeNumber(val)
    if isinstance(val, str):
        return RuntimeString(val)

    if isinstance(val, callable):
        return BuiltinFunction(val)


THE_STACK = []
def try_pop(arg, env, runtime: 'interpreter.Interpreter'):
    if len(THE_STACK) == 0:
        return RuntimeUnit()
    
    val = THE_STACK.pop()
    
    runtime.visit_function_application(env, FunctionApplication(val, arg), visit_arg=False)
    
    return RuntimeUnit()

def get_cur_line(rt: 'interpreter.Interpreter'):
    return RuntimeNumber(rt.current_line)

def write_to_mut_box(box: RuntimeMutableBox, *_):
    if not isinstance(box, RuntimeMutableBox):
        raise RuntimeTypeError(f"Expected mutable box, got {type(box)}")
    return BuiltinFunction(lambda arg, *_: box.write(arg), True)
    

def get_length(arg: MLType, *_):
    match arg:
        case RuntimeString(value):
            return RuntimeNumber(len(value))
        case RuntimeListType(value):
            return RuntimeNumber(len(value))
        case RuntimeNumber(value):
            return len(str(value))
        case _:
            return RuntimeNumber(0)

# HACK: Using string comparison for now because it'll work. It's really slow though.
std_funcs = {
    '?!': BuiltinFunction(lambda arg, *_: print(arg)),
    '+': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value + x.value)), False),
    '*': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value * x.value)), False),
    '-': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value - x.value)), False),
    '/': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value / x.value)), False),
    '%': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value % x.value)), False),
    '=': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.to_string() == x.to_string())), False),
    '>': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value > x.value)), False),
    '≥': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value >= x.value)), False),
    '<': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value < x.value)), False),
    '≤': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value <= x.value)), False),
    '≠': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.to_string() != x.to_string())), False), 
    
    '->': BuiltinFunction(lambda arg, *_: get_length(arg), False),
    
    # Get current line
    '[?]': BuiltinFunction(lambda arg, env, runtime: get_cur_line(runtime)),
    
    # Stack functions
    '|<|': BuiltinFunction(lambda arg, *_: THE_STACK.append(arg)),
    '|>|': BuiltinFunction(lambda arg, env, runtime: try_pop(arg, env, runtime)),
    
    # Mutable box functions
    '!': BuiltinFunction(lambda arg, *_: RuntimeMutableBox(arg), True),
    '!<': BuiltinFunction(lambda arg, *_: write_to_mut_box(arg), True),
    '!?': BuiltinFunction(lambda arg, *_: arg.value, True),
    
    '??': BuiltinFunction(lambda arg, *_: arg.to_string(), False),
}