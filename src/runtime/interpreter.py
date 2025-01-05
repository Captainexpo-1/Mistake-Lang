from runtime.environment import Environment
from runtime.runtime_types import *
import time

class ReturnValueException(Exception):
    def __init__(self, value: MLType):
        self.value = value

class Interpreter:
    def __init__(self):
        self.global_environment = Environment(None)

    def execute(self, ast: ASTNode):
        for node in ast:
            self.visit(node, self.global_environment, ctx={'is_imp': True, 'allow_side_effects': False})
        return self.global_environment
    
    def visit(self, node: ASTNode, env: Environment, ctx):
        if node.type == NodeType.S_VARIABLE_DECLARATION:
            self.visit_variable_declaration(node, env, ctx)
        elif node.type == NodeType.E_BLOCK:
            try:
                self.visit_block(node, env, ctx)
            except ReturnValueException as e:
                return e.value
        elif node.type == NodeType.S_FUNCTION_CALL:
            return self.visit_function_call(node, env, ctx)
        elif node.type == NodeType.E_STRING:
            return node.value
        elif node.type == NodeType.E_NUMBER:
            return node.value
        elif node.type == NodeType.E_FUNCTION_DECLARATION:
            return self.visit_function_declaration(node, env, ctx)
        else:
            raise NotImplementedError(f"Node type {node.type} not implemented")
    
    def parse_lifetime(self, node: ASTNode, lt: str):
        if lt == 'inf': return Lifetime(0, LifetimeType.INFINITE)
        end = lt[-1]
        value = float(lt[:-1])
        
        if end == 's': return Lifetime(value, LifetimeType.SECONDS, time.process_time())
        if end == 'l': return Lifetime(value, LifetimeType.LINES, start=node.line)
        if end == 'u': return Lifetime(value, LifetimeType.TIMESTAMP)
        
        raise NotImplementedError(f"Invalid lifetime duration {lt}")
    
    def visit_variable_declaration(self, node: ASTNode, env: Environment, ctx: dict[str, any]): 
        is_pub, value, lifetime = node.children
        name = node.value
        
        value = self.visit(value, env, ctx)
        
        lifetime = self.parse_lifetime(node, lifetime)
        
        env.add_variable(name, value, lifetime)
    
    def visit_function_declaration(self, node: ASTNode, env: Environment, ctx: dict[str, any]):
        ids = node.value
        impure, body = node.children
        name = ids
        
        return Function(name, body, impure)
    
    def visit_block(self, node: ASTNode, env: Environment, ctx: dict[str, any]):
        new_env = Environment(env)
        last = None
        for child in node.children:
            last = self.visit(child, new_env, ctx)
        raise ReturnValueException(last)
    
    def visit_function_call(self, node: ASTNode, env: Environment, ctx: dict[str, any]):
        name = node.value
        if not env.get_variable(name):
            raise VariableNotFoundError(f"Function {name} not found")
        
        function = env.get_variable(name)
        print(function)
        if not isinstance(function, Function) and not isinstance(function, BuiltinFunction):
            raise TypeError(f"Variable {name} is not a function")
        
        if isinstance(function, BuiltinFunction):
            return function.func(node.children, env)
        
        new_env = Environment(env)
        for child in node.children:
            self.visit(child, new_env, 
                ctx={
                    'is_imp': False, 
                    'allow_side_effects': function.impure
                }
            )