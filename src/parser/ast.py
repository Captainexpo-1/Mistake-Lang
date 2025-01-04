from enum import Enum
from typing import List

class NodeType(Enum):
    S_FUNCTION_CALL = 0
    S_VARIABLE_DECLARATION = 1
    E_BLOCK = 2
    E_STRING = 3
    E_NUMBER = 4
    E_FUNCTION_DECLARATION = 5
class ASTNode:
    def __init__(self, type: NodeType, value: any, children: List['ASTNode'] = []):
        self.value = value
        self.type = type
        self.children = [i for i in children if i]
        
    def __str__(self) -> str: return f"Node({self.type}: \"{self.value}\" & {self.children if self.children else 'none'})"
    def __repr__(self) -> str: return str(self)
    
    def add_child(self, child: 'ASTNode'):
        if child != None: self.children.append(child)