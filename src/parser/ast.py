from enum import Enum
from typing import List

class ASTNode:
    def __init__(self): pass
    def __str__(self): pass
    def __repr__(self): return self.__str__()

class VariableAccess(ASTNode):
    def __init__(self, name: str):
        self.name = name
        
    def __str__(self):
        return f"VariableAccess({self.name})"
    
class FunctionApplication(ASTNode):
    def __init__(self, called: ASTNode, parameter: str):
        self.called = called
        self.parameter = parameter
        
    def __str__(self):
        return f"FunctionApplication({self.called}, {self.parameter})"
    
class Number(ASTNode):
    def __init__(self, value: float):
        self.value = float(value)
        
    def __str__(self):
        return str(self.value)
    
class String(ASTNode):
    def __init__(self, value: str):
        self.value = value
        
    def __str__(self):
        return self.value
    
class Boolean(ASTNode):
    def __init__(self, value: bool):
        self.value = value
        
    def __str__(self):
        return str(self.value)
    
class Unit(ASTNode):
    def __init__(self):
        pass
    
    def __str__(self):
        return "Unit"
    
class Block(ASTNode):
    def __init__(self, body: List[ASTNode]):
        self.body = body
        
    def __str__(self):
        return f"Block({self.body})"
    
class VariableDeclaration(ASTNode):
    def __init__(self, name: str, value: ASTNode, lifetime: str = "inf"):
        self.name = name
        self.value = value
        self.lifetime = lifetime
        
    def __str__(self):
        return f"VariableDeclaration({self.name}, value={self.value}, lifetime={self.lifetime})"
    
class FunctionDeclaration(ASTNode):
    def __init__(self, parameter: str, body: ASTNode, impure: bool = False):
        self.parameter = parameter
        self.body = body
        self.impure = impure
        
    def __str__(self):
        return f"FunctionDeclaration({self.parameter}, body={self.body}, impure={self.impure})"
    
