from typing import List
from parser.ast import ASTNode
from enum import Enum
from runtime.errors.runtime_errors import InvalidLifetimeError
from datetime import datetime
import time
import runtime.environment as rte


class MLType:
    def to_string(self):
        raise NotImplementedError("to_string method not implemented")

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()


class RuntimeUnit(MLType):
    def __init__(self):
        pass

    def to_string(self):
        return "Null"


class RuntimeNumber(MLType):
    def __init__(self, value: float):
        self.value = value

    def to_string(self):
        return f"Number({self.value})"


class RuntimeString(MLType):
    def __init__(self, value: str):
        self.value = value

    def to_string(self):
        return f'String("{self.value}")'


class RuntimeBoolean(MLType):
    def __init__(self, value: bool | str):
        self.value = value in ["true", "True", True]

    def to_string(self):
        return f"Boolean({self.value})"

    def __eq__(self, other):
        ov = other.value if isinstance(other, RuntimeBoolean) else other
        return self.value == ov


class Function(MLType):
    def __init__(self, parameter: str, body: List[ASTNode], impure: bool = False):
        self.param = parameter
        self.body = body
        self.impure = impure

    def to_string(self):
        return (
            f"{'Impure' if self.impure else ''}Function({self.param}, body={self.body})"
        )


class ClassType(MLType):
    def __init__(self, name: str, members: dict[str, MLType], public_members: set[str]):
        self.name = name
        self.members = members
        self.public_members = public_members

    def to_string(self):
        return f"Class({self.name}, fields={self.members}, public_fields={self.public_members})"


class ClassInstance(MLType):
    def __init__(
        self,
        class_type: ClassType,
        members: dict[str, MLType],
        environment: "rte.Environment",
    ):
        self.class_type = class_type
        self.members = members

        self.environment = environment
        # print("CLASS INSTANCE ENVIRONMENT", self.environment)

    def to_string(self):
        return f"InstanceOf({self.class_type.name}, fields={self.members})"


class BuiltinFunction(MLType):
    def __init__(self, func: callable, is_impure=True):
        self.func = func
        self.impure = is_impure

    def to_string(self):
        return f"BuiltinFunction({self.func}, impure={self.impure})"


class LifetimeType(Enum):
    DMS_TIMESTAMP = 0  # given in miliseconds since jan 1st 2020
    DECIMAL_SECONDS = 1
    LINES = 2
    INFINITE = 3
    TICKS = 4


def get_timestamp():
    reference_date = datetime(2020, 1, 1)
    current_time = datetime.now()
    time_difference = current_time - reference_date
    milliseconds = int(time_difference.total_seconds() * 1000)
    decimal_milliseconds = int(milliseconds * 0.864)
    return decimal_milliseconds


class Lifetime(MLType):
    def __init__(self, type: LifetimeType, value: float, start: float = 0):
        self.value = value
        self.type = type
        self.start = start

        if self.value < 0:
            raise InvalidLifetimeError("Lifetime value must be greater than 0")
        if int(self.value) != self.value and self.type in [
            LifetimeType.LINES,
            LifetimeType.DMS_TIMESTAMP,
        ]:
            raise InvalidLifetimeError("Lifetime value must be an integer")
        elif int(self.value) == self.value:
            self.value = int(self.value)

    def to_string(self):
        return f"Lifetime({self.value}, {self.type})"

    def is_expired(self, line=None):
        match self.type:
            case LifetimeType.INFINITE:
                return False
            case LifetimeType.DMS_TIMESTAMP:
                return get_timestamp() >= self.value
            case LifetimeType.DECIMAL_SECONDS:
                return (
                    (time.process_time() * 0.864) - self.start >= self.value
                )  # 0.864 is the conversion from seconds to decimal seconds
            case LifetimeType.TICKS:
                return time.process_time() * 20 - self.start >= self.value
            case LifetimeType.LINES:
                if line is None:
                    raise InvalidLifetimeError(
                        "Line number must be provided for line lifetime"
                    )
                return line - self.start >= self.value


class PyNativeObject(MLType):
    def __init__(self, obj):
        self.obj = obj

    def to_string(self):
        return f"PythonNativeObject({self.obj})"
    
class RuntimeMutableBox(PyNativeObject):
    def __init__(self, value: any):   
        self.value = value
        
    def to_string(self):
        return f"MutableBox({self.value})"
    
    def write(self, value):
        self.value = value
        return RuntimeUnit()
    
class RuntimeListType(PyNativeObject):
    def __init__(self, list: dict[int, MLType]):
        self.list = list
    
    def get(self, idx: int):
        if idx < 1:
            raise IndexError("Index must be greater than 0")
        return self.list.get(idx, RuntimeUnit())
    
    def length(self):
        i = 0
        while (i+1) in self.list:
            i += 1
        return RuntimeNumber(i)
    
    def set(self, idx: int, value: MLType):
        if idx < 1:
            raise IndexError("Index must be greater than 0")
        self.list[idx] = value
        return RuntimeUnit()
    
    def to_string(self):
        return f"List({self.list})"