from runtime.environment import Environment
from runtime.runtime_types import *
from parser.ast import *
import time

class ReturnValueException(Exception):
    def __init__(self, value: MLType):
        self.value = value

class Interpreter:
    def __init__(self):
        self.global_environment = Environment(None)

    def execute(self, ast: ASTNode):
        return self.global_environment
    