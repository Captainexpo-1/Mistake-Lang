import re
from mistake.runtime.errors.runtime_errors import *
from mistake.runtime.runtime_types import *
import mistake.runtime.environment as environment
import mistake.runtime.interpreter as interpreter
from mistake.parser.ast import *
import requests

def fn_bang_qmark(arg: MLType, *_):
    print(arg)

def get_type(val: any):
    if isinstance(val, bool):
        return RuntimeBoolean(val)
    if isinstance(val, int) or isinstance(val, float):
        return RuntimeNumber(val)
    if isinstance(val, str):
        return RuntimeString(val)
    if callable(val):
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
        if isinstance(box, ClassMemberReference):
            return BuiltinFunction(lambda arg, *_: box.set(arg), True)
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
        case RuntimeMatchObject(value):
            return RuntimeNumber(len(value.groups()))
        case _:
            return RuntimeNumber(0)

def create_regex_func(arg: RuntimeString, *_):
    try:
        comp = re.compile(arg.value)
        return BuiltinFunction(
            lambda arg, *_: RuntimeListType({(i+1):RuntimeMatchObject(m) for i,m in enumerate(comp.findall(arg.value))}),
            imp=False
        )   
    except re.error:
        return RuntimeUnit()


def get_group_from_match(arg: RuntimeMatchObject, *_):
    return BuiltinFunction(lambda x, *_: RuntimeString(arg.group(x.value)), imp=False)

def get_string_from_match(arg: RuntimeMatchObject, *_):
    return RuntimeString(str(arg.match))
std_funcs = {
    '?!': BuiltinFunction(lambda arg, *_: print(arg)),
    '+': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value + x.value), imp=False), imp=False),
    '*': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value * x.value), imp=False), imp=False),
    '-': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value - x.value), imp=False), imp=False),
    '/': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value / x.value), imp=False), imp=False),
    '%': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value % x.value), imp=False), imp=False),
    '=': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.to_string() == x.to_string())), imp=False),
    '>': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value > x.value), imp=False), imp=False),
    '≥': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value >= x.value), imp=False), imp=False),
    '<': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value < x.value), imp=False), imp=False),
    '≤': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.value <= x.value), imp=False), imp=False),
    '≠': BuiltinFunction(lambda arg, *_: BuiltinFunction(lambda x, *_: get_type(arg.to_string() != x.to_string()), imp=False), imp=False), 
    '->': BuiltinFunction(lambda arg, *_: get_length(arg), imp=False),
    '[?]': BuiltinFunction(lambda arg, env, runtime: get_cur_line(runtime), imp=False),
    '|<|': BuiltinFunction(lambda arg, *_: THE_STACK.append(arg), imp=True),
    '|>|': BuiltinFunction(lambda arg, env, runtime: try_pop(arg, env, runtime), imp=True),
    '!': BuiltinFunction(lambda arg, *_: RuntimeMutableBox(arg), imp=True),
    '!<': BuiltinFunction(lambda arg, *_: write_to_mut_box(arg), imp=True),
    '!?': BuiltinFunction(lambda arg, *_: arg.value, imp=True),
    '??': BuiltinFunction(lambda arg, *_: arg.to_string(), imp=False),
    '/?/': BuiltinFunction(create_regex_func, imp=False),
    '/>?/': BuiltinFunction(get_group_from_match, imp=False),
    '/>"/': BuiltinFunction(get_string_from_match, imp=False),
    
    # Lists
    '[!]':  BuiltinFunction(lambda arg, *_: RuntimeListType({1: arg} if not isinstance(arg, RuntimeUnit) else {}), imp=False),
    '[<]':  BuiltinFunction(lambda arg, *_: 
                BuiltinFunction(
                    lambda x1, *_: 
                        BuiltinFunction(
                            lambda x2, *_: arg.set(x1.value, x2),
                            imp=False
                        ),
                    imp=False
                )
            ),
    '[>]': BuiltinFunction(lambda arg, *_: 
                BuiltinFunction(
                    lambda x1, *_: arg.get(x1.value),
                    imp=False
                )
            ),

    '<!>': BuiltinFunction(lambda *_: RuntimeUnit(), imp=False, subtype="asynccall"),
    
    '<-%?-': BuiltinFunction(lambda arg, *_: requests.get(arg.value).text, imp=True), # GET request
    '<-%!-': BuiltinFunction(lambda arg, *_: requests.post(arg.value).text, imp=True), # POST request
    
    '=!=': BuiltinFunction(lambda arg, env, runtime: runtime.create_channel(), imp=True), # Create a channel
    '<<': BuiltinFunction(lambda arg, env, runtime: BuiltinFunction(lambda x, *_: runtime.send_to_channel(arg, x), imp=True)), # Send to channel
    '>>': BuiltinFunction(lambda arg, env, runtime: runtime.receive_from_channel(arg), imp=True), # Receive from channel
}
