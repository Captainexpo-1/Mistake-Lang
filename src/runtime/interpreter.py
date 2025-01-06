from runtime.environment import Environment
from runtime.runtime_types import *
from runtime.errors.runtime_errors import *
from tokenizer.token import Token, TokenType
from parser.ast import *
from parser.parser import Parser
from typing import List

import time

class ReturnValueException(Exception):
    def __init__(self, value: MLType):
        self.value = value

class Interpreter:
    def __init__(self):
        self.parser = Parser()
        self.global_environment = Environment(None)

    def visit_function_application(self, env: Environment, node: FunctionApplication):
        
        function = self.visit_node(node.called, env)
        if not isinstance(function, Function) and not isinstance(function, BuiltinFunction):
            raise RuntimeError(f"Variable {node.called} is not a function, but a {type(function)}")
        
        param = self.visit_node(node.parameter, env)
        
        if isinstance(function, BuiltinFunction):
            return function.func(param)
        
        new_env = Environment(env)
        new_env.add_variable(function.param, param, Lifetime(LifetimeType.INFINITE, 0))
        if isinstance(function.body[0], Token): 
            function.body = self.parser.parse(function.body)
        return self.visit_block(function.body[0], new_env, create_env=False)
    
    def visit_function_declaration(self, node: FunctionDeclaration, env: Environment):
        params = node.parameters
        # curry the function
        def get_curried(params, body):
            if len(params) == 1:
                return Function(params[0], body)
            return Function(params[0], [get_curried(params[1:], body)])
        
        return get_curried(params, node.body)
    
    def visit_block(self, node: Block, env: Environment, create_env=True):
        new_env = Environment(env) if create_env else env
        for statement in node.body[:-1]:
            self.visit_node(statement, new_env)

        return self.visit_node(node.body[-1], new_env)
    
    def get_lifetime(self, lifetime: str, node: ASTNode):
        if lifetime == "inf":
            return Lifetime(LifetimeType.INFINITE, 0)
        match lifetime[-1]:
            case 's':
                return Lifetime(LifetimeType.SECONDS, int(lifetime[:-1]), time.process_time() * 0.864)
            case 'l':
                return Lifetime(LifetimeType.LINES, int(lifetime[:-1]), 0) # TODO: ACTUAL LINE STUFF 
            case 'u':
                return Lifetime(LifetimeType.TIMESTAMP, int(lifetime[:-1]), get_timestamp())
            case _:
                raise RuntimeError(f"Invalid lifetime {lifetime}")
    
    def visit_node(self, node: ASTNode, env: Environment, implicit=False):
        #print(f"Visiting node {node} with:\n{env}")
        if isinstance(node, Unit):
            return RuntimeNull()
        if isinstance(node, Number):
            return RuntimeNumber(node.value)
        if isinstance(node, String):
            return RuntimeString(node.value)
        if isinstance(node, Boolean):
            return RuntimeBoolean(node.value)
        if isinstance(node, Function):
            return node
        if isinstance(node, VariableAccess):
            return env.get_variable(node.name)
        if isinstance(node, FunctionApplication):
            return self.visit_function_application(env, node)
        if isinstance(node, Block):
            return self.visit_block(node, env)
        if isinstance(node, VariableDeclaration):
            value = self.visit_node(node.value, env)
            env.add_variable(node.name, value, self.get_lifetime(node.lifetime, node))
            return value
        if isinstance(node, FunctionDeclaration):
            return self.visit_function_declaration(node, env)
        raise RuntimeError(f"Node {node} not implemented")
    
    def execute(self, ast: List[ASTNode]):
        self.ast = ast
        for node in ast:
            self.visit_node(node, self.global_environment, True)
        return self.global_environment
    