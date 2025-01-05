from typing import List
from parser.ast import ASTNode, NodeType
from enum import Enum
from runtime.errors.runtime_errors import *
import datetime, time
class MLType: 
    def to_string(self): 
        raise NotImplementedError("to_string method not implemented")
    def __str__(self): 
        return self.to_string()
    def __repr__(self):
        return self.to_string()

class Number(MLType):
    def __init__(self, value: float): 
        self.value = value
    def to_string(self): 
        return self.value
    
class String(MLType):
    def __init__(self, value: str): 
        self.value = value
    def to_string(self): 
        return self.value
    
class Boolean(MLType):
    def __init__(self, value: bool|str): 
        self.value = value in ['true', 'True', True]
    def to_string(self): 
        return self.value
    
class Function(MLType):
    def __init__(self, parameters: str, body: List[ASTNode], impure: bool = False, is_std: tuple[bool, callable] = (False, None)): 
        self.name = parameters
        self.body = body
        self.impure = impure
        self.is_std = is_std    
    def to_string(self): 
        return f"{'Impure' if self.impure else ''}Function({self.name}, body={self.body}, std={self.is_std})"

class BuiltinFunction(MLType):
    def __init__(self, func: callable): 
        self.func = func
    def to_string(self): 
        return f"BuiltinFunction({self.func})"

class LifetimeType(Enum):
    TIMESTAMP = 0 # given in miliseconds since jan 1st 2020   
    SECONDS = 1
    LINES = 2
    INFINITE = 3

def get_timestamp():
    reference_date = datetime(2020, 1, 1)
    current_time = datetime.utcnow()
    time_difference = current_time - reference_date
    milliseconds = int(time_difference.total_seconds() * 1000)
    decimal_milliseconds = int(milliseconds * 0.864)
    return decimal_milliseconds

class Lifetime(MLType):
    def __init__(self, value: float, type: LifetimeType, start: float = 0): 
        self.value = value
        self.type = type
        self.start = start
        
        if self.value < 0:
            raise InvalidLifetimeError("Lifetime value must be greater than 0")
        if int(self.value) != self.value and self.type in [LifetimeType.LINES, LifetimeType.TIMESTAMP]:
            raise InvalidLifetimeError("Lifetime value must be an integer")
        elif int(self.value) == self.value:
            self.value = int(self.value)
        
    def to_string(self): 
        return f"Lifetime({self.value}, {self.type})"
    
    def is_expired(self, line=None):
        match self.type:
            case LifetimeType.INFINITE:
                return False
            case LifetimeType.TIMESTAMP:
                return get_timestamp() >= self.value
            case LifetimeType.SECONDS:
                return (time.process_time()*0.864) - self.start >= self.value # 0.864 is the conversion from seconds to decimal seconds
            case LifetimeType.LINES:
                if line == None:
                    raise InvalidLifetimeError("Line number must be provided for line lifetime")
                return line - self.start >= self.value
            