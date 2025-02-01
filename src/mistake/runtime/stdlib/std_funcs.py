import re
import time
import gevent
import mistake.runtime.interpreter as interpreter

from mistake.parser.ast import (
    FunctionApplication,
)
from mistake.runtime.errors.runtime_errors import (
    RuntimeTypeError,
)
from mistake.runtime.runtime_types import (
    RuntimeBoolean,
    RuntimeNumber,
    RuntimeString,
    RuntimeUnit,
    RuntimeMutableBox,
    RuntimeListType,
    RuntimeMatchObject,
    RuntimeTask,
    RuntimeDictType,
    BuiltinFunction,
    Function,
    MLType,
    convert_type,
    de_runtime_dictify,
    runtime_dictify,
)
from mistake.runtime.stdlib.networking import (
    create_TCP_server,
    create_UDP_server,
    create_TCP_socket,
    create_UDP_socket,
)
from mistake.utils import from_decimal_seconds, RUNTIME_USE_VULKAN

if RUNTIME_USE_VULKAN:
    import mistake.runtime.stdlib.vulkan_api as vstd
import os

from mistake.runtime.stdlib.airtable_api import (
    all_bases,
    create_airtable_api_instance,
    create_base,
    list_table_records,
    get_record,
    create_record,
    update_record,
    delete_record,
    new_record,
    base_schema,
    create_new_field,
    update_field,
)

from typing import Any, Callable


def get_type(val: Any):
    if isinstance(val, bool):
        return RuntimeBoolean(val)
    if isinstance(val, int) or isinstance(val, float):
        return RuntimeNumber(val)
    if isinstance(val, str):
        return RuntimeString(val)
    if callable(val):
        return BuiltinFunction(val)


_STACK = []
PRINT_CALLBACK = None

def set_print_callback(callback: Callable[[str], None]):
    global PRINT_CALLBACK
    PRINT_CALLBACK = callback
    

def try_pop(arg, env, runtime: "interpreter.Interpreter"):
    if len(_STACK) == 0:
        return RuntimeUnit()

    val = _STACK.pop()

    runtime.visit_function_application(
        env, FunctionApplication(val, arg), visit_arg=False
    )

    return RuntimeUnit()


def get_cur_line(rt: "interpreter.Interpreter"):
    return RuntimeNumber(rt.current_line)


def write_to_mut_box(box: RuntimeMutableBox, *_):
    if not isinstance(box, RuntimeMutableBox):
        raise RuntimeTypeError(f"Expected mutable box, got {type(box)}")
    return BuiltinFunction(lambda arg, *_: box.write(arg), True)


def get_length(arg: MLType, *_):
    match arg:
        case RuntimeString(value):
            # Length of string in bytes
            return RuntimeNumber(len(value.encode()))
        case RuntimeListType(value):
            return RuntimeNumber(len(value))
        case RuntimeNumber(value):
            return len(str(value))
        case RuntimeMatchObject(value):
            return RuntimeNumber(len(value.groups()))
        case RuntimeTask(_, start_time):
            return RuntimeNumber(time.time() - start_time)
        case _:
            return RuntimeNumber(0)


def create_regex_func(arg: RuntimeString, *_):
    try:
        comp = re.compile(arg.value)
        return BuiltinFunction(
            lambda arg, *_: RuntimeListType(
                {
                    (i + 1): RuntimeMatchObject(m)
                    for i, m in enumerate(comp.findall(arg.value))
                }
            ),
            imp=False,
        )
    except re.error:
        return RuntimeUnit()


def get_group_from_match(arg: RuntimeMatchObject, *_):
    return BuiltinFunction(lambda x, *_: RuntimeString(arg.group(x.value)), imp=False)


def get_string_from_match(arg: RuntimeMatchObject, *_):
    return RuntimeString(str(arg.match))


def new_task_from_function_app(
    function: Function, env, runtime: "interpreter.Interpreter", delay: float = 0.0
):
    def task():
        gevent.sleep(from_decimal_seconds(delay))
        runtime.visit_function_application(
            env, FunctionApplication(function, RuntimeUnit()), visit_arg=False
        )

    spawn = gevent.spawn(task)
    runtime.add_task(spawn)
    return RuntimeTask(spawn)


def new_task_from_func(
    func: callable, runtime: "interpreter.Interpreter", delay: float = 0.0
):
    def task():
        gevent.sleep(from_decimal_seconds(delay))
        func()

    spawn = gevent.spawn(task)
    runtime.add_task(spawn)
    return RuntimeTask(spawn)


def is_truthy(arg: MLType, *_):
    if isinstance(arg, RuntimeBoolean):
        return arg.value
    return not isinstance(arg, RuntimeUnit)


def assert_true(arg: MLType, *_):
    if not is_truthy(arg):
        raise AssertionError("Assertion failed")
    return RuntimeUnit()

def mlprint(arg: MLType, *_):
    if PRINT_CALLBACK:
        PRINT_CALLBACK(arg.to_string())
    else:
        print(arg)
    return RuntimeUnit()
    

std_funcs = {
    "?!": BuiltinFunction(lambda arg, *_: mlprint(arg)),
    "+": BuiltinFunction(
        lambda arg, *_: BuiltinFunction(
            lambda x, *_: get_type(arg.value + x.value), imp=False
        ),
        imp=False,
    ),
    "*": BuiltinFunction(
        lambda arg, *_: BuiltinFunction(
            lambda x, *_: get_type(arg.value * x.value), imp=False
        ),
        imp=False,
    ),
    "-": BuiltinFunction(
        lambda arg, *_: BuiltinFunction(
            lambda x, *_: get_type(arg.value - x.value), imp=False
        ),
        imp=False,
    ),
    "/": BuiltinFunction(
        lambda arg, *_: BuiltinFunction(
            lambda x, *_: get_type(arg.value / x.value), imp=False
        ),
        imp=False,
    ),
    "%": BuiltinFunction(
        lambda arg, *_: BuiltinFunction(
            lambda x, *_: get_type(arg.value % x.value), imp=False
        ),
        imp=False,
    ),
    "=": BuiltinFunction(
        lambda arg, *_: BuiltinFunction(
            lambda x, *_: get_type(arg.to_string() == x.to_string())
        ),
        imp=False,
    ),
    ">": BuiltinFunction(
        lambda arg, *_: BuiltinFunction(
            lambda x, *_: get_type(arg.value > x.value), imp=False
        ),
        imp=False,
    ),
    "≥": BuiltinFunction(
        lambda arg, *_: BuiltinFunction(
            lambda x, *_: get_type(arg.value >= x.value), imp=False
        ),
        imp=False,
    ),
    "<": BuiltinFunction(
        lambda arg, *_: BuiltinFunction(
            lambda x, *_: get_type(arg.value < x.value), imp=False
        ),
        imp=False,
    ),
    "≤": BuiltinFunction(
        lambda arg, *_: BuiltinFunction(
            lambda x, *_: get_type(arg.value <= x.value), imp=False
        ),
        imp=False,
    ),
    "≠": BuiltinFunction(
        lambda arg, *_: BuiltinFunction(
            lambda x, *_: get_type(arg.to_string() != x.to_string()), imp=False
        ),
        imp=False,
    ),
    "->": BuiltinFunction(lambda arg, *_: get_length(arg), imp=False),
    "[?]": BuiltinFunction(lambda arg, env, runtime: get_cur_line(runtime), imp=False),
    "|<|": BuiltinFunction(lambda arg, *_: _STACK.append(arg), imp=True),
    "|>|": BuiltinFunction(
        lambda arg, env, runtime: try_pop(arg, env, runtime), imp=True
    ),
    "!": BuiltinFunction(lambda arg, *_: RuntimeMutableBox(arg), imp=True),
    "!<": BuiltinFunction(lambda arg, *_: write_to_mut_box(arg), imp=True),
    "!?": BuiltinFunction(lambda arg, *_: arg.value, imp=True),
    "/?/": BuiltinFunction(create_regex_func, imp=False),
    "/>?/": BuiltinFunction(get_group_from_match, imp=False),
    '/>"/': BuiltinFunction(get_string_from_match, imp=False),
    "??": BuiltinFunction(lambda arg, *_: RuntimeString(arg.to_string()), imp=False),
    "!!": BuiltinFunction(lambda arg, *_: assert_true(arg), imp=False),
    # Lists
    "[!]": BuiltinFunction(lambda *args: RuntimeListType(), imp=False),
    "[<]": BuiltinFunction(
        lambda arg, *_: BuiltinFunction(
            lambda index, *_: BuiltinFunction(
                lambda value, *_: arg.set(index.value, value), imp=False
            ),
            imp=False,
        )
    ),
    "[>]": BuiltinFunction(
        lambda arg, *_: BuiltinFunction(lambda x1, *_: arg.get(x1.value), imp=False)
    ),
    "[/]": BuiltinFunction(
        lambda arg0, *_: BuiltinFunction(
            lambda arg1, env, runtime: new_task_from_function_app(
                arg1, env, runtime, arg0.value
            ),
            imp=True,
        )
    ),
    "<!>": BuiltinFunction(
        lambda arg, env, runtime: new_task_from_function_app(arg, env, runtime, 0),
        imp=False,
    ),
    "</>": BuiltinFunction(lambda arg, env, runtime: arg.kill(), imp=False),
    "=!=": BuiltinFunction(
        lambda arg, env, runtime: runtime.create_channel(), imp=True
    ),  # Create a channel
    "<<": BuiltinFunction(
        lambda arg, env, runtime: BuiltinFunction(
            lambda x, *_: runtime.send_to_channel(arg, x), imp=True
        )
    ),  # Send to channel
    ">>": BuiltinFunction(
        lambda arg, env, runtime: runtime.receive_from_channel(arg), imp=True
    ),  # Receive from channel
    # NETWORKING
    #'<=#=>': BuiltinFunction(lambda arg, env, runtime: create_TCP_server(arg, env, runtime), imp=True),
    "<=?=>": BuiltinFunction(
        lambda arg, env, runtime: create_UDP_server(arg, env, runtime), imp=True
    ),
    "<=#=>": BuiltinFunction(
        lambda arg, env, runtime: create_TCP_server(arg, env, runtime), imp=True
    ),
    "<=?=": BuiltinFunction(
        lambda arg, env, runtime: create_UDP_socket(arg, env, runtime), imp=True
    ),
    "<=#=": BuiltinFunction(
        lambda arg, env, runtime: create_TCP_socket(arg, env, runtime), imp=True
    ),
    "==>#": BuiltinFunction(
        lambda x0, *_: BuiltinFunction(
            lambda x1, env, runtime: x0.bind_port(x1), imp=True
        )
    ),
    "==>?": BuiltinFunction(
        lambda x0, *_: BuiltinFunction(lambda x1, env, runtime: x0.set_hostname(x1)),
        imp=True,
    ),
    "==>!": BuiltinFunction(
        lambda x0, *_: BuiltinFunction(
            lambda x1, env, runtime: x0.set_callback(
                lambda callback_arg: runtime.visit_function_application(
                    env, FunctionApplication(x1, callback_arg), visit_arg=False
                )
            ),
            imp=True,
        )
    ),
    ">|<": BuiltinFunction(lambda arg, *_: arg.close(), imp=True),
    # DICTIONARIES
    "{+}": BuiltinFunction(lambda *_: RuntimeDictType(), imp=False),
    ">{}": BuiltinFunction(
        lambda d, *_: BuiltinFunction(
            lambda key, *_: BuiltinFunction(lambda value, *_: d.set(key, value))
        ),
        imp=False,
    ),
    "<{}": BuiltinFunction(
        lambda d, *_: BuiltinFunction(lambda key, *_: d.get(key), imp=False)
    ),
    # MISC HELPERS
    '>"<': BuiltinFunction(lambda arg, *_: RuntimeString(arg.value.strip()), imp=False),
    # AIRTABLE
    "{>!<}": BuiltinFunction(
        lambda arg, *_: create_airtable_api_instance(arg)
    ),  # create airtable api
    "{!}": BuiltinFunction(lambda arg, *_: create_base(arg)),  # create base
    "{?}": BuiltinFunction(
        lambda table, *_: list_table_records(table)
    ),  # get all records
    "{>}": BuiltinFunction(
        lambda table, *_: BuiltinFunction(lambda id, *_: get_record(table, id))
    ),  # get record
    "{<}": BuiltinFunction(
        lambda table, *_: BuiltinFunction(
            lambda record, *_: create_record(table, record)
        )
    ),  # put record
    "{!": BuiltinFunction(
        lambda fields, *_: new_record(de_runtime_dictify(fields))
    ),  # create local record instance
    "{-}": BuiltinFunction(
        lambda table, *_: BuiltinFunction(
            lambda record_id, *_: delete_record(table, record_id.value)
        )
    ),  # delete record
    "{\\}": BuiltinFunction(
        lambda table, *_: BuiltinFunction(
            lambda record, *_: update_record(table, record)
        )
    ),  # update record
    # Schema editing
    "{{?": BuiltinFunction(
        lambda table, *_: RuntimeDictType(runtime_dictify(table.table.schema().dict()))
    ),  # get schema
    "{{+": BuiltinFunction(
        lambda table, *_: BuiltinFunction(
            lambda field, *_: BuiltinFunction(
                lambda field_type, *_: BuiltinFunction(
                    lambda options, *_: create_new_field(
                        table, field, field_type, options
                    )
                )
            )
        )
    ),  # add field    # Record editing
    "{{=": BuiltinFunction(
        lambda table, *_: BuiltinFunction(
            lambda field_id, *_: BuiltinFunction(
                lambda new_options, *_: update_field(table, field_id, new_options)
            )
        )
    ),  # update field
    # RECORD EDITING
    "{<": BuiltinFunction(
        lambda record, *_: BuiltinFunction(
            lambda field, *_: BuiltinFunction(
                lambda value, *_: record.set_field(field, value)
            )
        )
    ),  # create airtable api
    "{>": BuiltinFunction(
        lambda record, *_: BuiltinFunction(lambda field, *_: field.fields[record])
    ),  # create airtable api
    "{#>": BuiltinFunction(lambda record, *_: convert_type(record.id)),  # get ID
    "{#<": BuiltinFunction(
        lambda record, *_: BuiltinFunction(lambda ID, *_: record.set_id(ID))
    ),  # set ID
    # BASE MANIPULATION
    "{}?": BuiltinFunction(lambda *args: all_bases(*args)),
    "{}??": BuiltinFunction(lambda base, *_: base_schema(base)),
    # ENV
    "[@@@]": BuiltinFunction(lambda key, *_: RuntimeString(os.getenv(key.value))),
}

if RUNTIME_USE_VULKAN:
    std_funcs.update(vstd.vulkan_std_funcs)
