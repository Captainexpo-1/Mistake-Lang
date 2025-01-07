from runtime.runtime_types import *
from runtime.errors.runtime_errors import *
from typing import List
from parser.ast import ASTNode
import runtime.stdlib.std_funcs as stdlib

class Environment:
    def __init__(self, parent: 'Environment'):
        self.variables: dict[str, MLType] = {}
        self.lifetimes: dict[str, Lifetime] = {}
        
        #print(f"Creating environment {id(self)} with parent {id(parent)}")
        self.parent = parent
        
    def get_variable(self, name: str, force_purity=True) -> MLType:
        if name in self.variables:
            if self.lifetimes[name].is_expired():
                del self.variables[name]
                del self.lifetimes[name]
                raise LifetimeExpiredError(f"Lifetime for variable {name} has expired")
            return self.variables[name]
        
        if self.parent and not force_purity:
            return self.parent.get_variable(name)
        
        if name in stdlib.std_funcs:
            return stdlib.std_funcs[name]
        
        raise VariableNotFoundError(f"Variable {name} not found in {self}")
    
    def add_variable(self, name: str, value: MLType, lifetime: Lifetime, ignore_duplicate=False):
        if not ignore_duplicate and name in self.variables:
            raise VariableAlreadyDefinedError(f"Variable {name} already defined in this scope")
        
        #print(f"Adding variable {name} with value {value} and lifetime {lifetime} to {id(self)}")
        
        self.variables[name] = value
        self.lifetimes[name] = lifetime
    
    def __repr__(self):
        out = "Environment(\n"
        for var in self.variables:
            out += f"   {var}: {self.variables[var].to_string()}\n"
            
        out += ")"
        return out
    
        