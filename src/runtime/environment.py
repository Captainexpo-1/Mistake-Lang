from runtime.runtime_types import *
from runtime.errors.runtime_errors import *
from typing import List
from parser.ast import ASTNode, NodeType


class Environment:
    def __init__(self, parent: 'Environment'):
        self.variables: dict[str, MLType] = {}
        self.lifetimes: dict[str, Lifetime] = {}
        self.parent = parent
        
    def get_variable(self, name: str) -> MLType:
        if name in self.variables:
            if self.lifetimes[name].is_expired():
                del self.variables[name]
                del self.lifetimes[name]
                raise LifetimeExpiredError(f"Lifetime for variable {name} has expired")
            return self.variables[name]
        
        if self.parent:
            return self.parent.get_variable(name)
        raise VariableNotFoundError(f"Variable {name} not found")
    
    def add_variable(self, name: str, value: MLType, lifetime: Lifetime):
        if name in self.variables:
            raise VariableAlreadyDefinedError(f"Variable {name} already defined in this scope")
        
        self.variables[name] = value
        self.lifetimes[name] = lifetime
    
    def __repr__(self):
        out = "Environment(\n"
        for var in self.variables:
            out += f"   {var}: {self.variables[var]}\n"
            
        out += ")"
        return out
        