import time
from parser.ast import *
from parser.parser import Parser
from typing import List

import runner
from runtime.environment import Environment
from runtime.errors.runtime_errors import RuntimeError
from runtime.runtime_types import *  # noqa: F403
from tokenizer.token import Token


class ReturnValueException(Exception):
    def __init__(self, value: MLType):
        self.value = value


class Interpreter:
    def __init__(self):
        self.parser = Parser()
        self.global_environment = Environment(None)
        self.current_line = 1
        self.files: dict[str, List[ASTNode]] = {}

    def visit_function_application(
        self, env: Environment, node: FunctionApplication, visit_arg=True
    ):
        function = self.visit_node(node.called, env)
        if not isinstance(function, Function) and not isinstance(
            function, BuiltinFunction
        ):
            raise RuntimeError(
                f"Variable {node.called} is not a function, but a {type(function)}"
            )

        param = self.visit_node(node.parameter, env) if visit_arg else node.parameter

        if isinstance(function, BuiltinFunction):
            return function.func(param, env, self)

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

    def get_lifetime(self, lifetime: str, *_):
        return (
            Lifetime(LifetimeType.INFINITE, 0)
            if lifetime == "inf"
            else (
                [
                    lambda: Lifetime(
                        LifetimeType.LINES, int(lifetime[:-1]), self.lines_executed
                    ),
                    lambda: Lifetime(
                        LifetimeType.DMS_TIMESTAMP, int(lifetime[:-1]), get_timestamp()
                    ),
                    lambda: Lifetime(
                        LifetimeType.TICKS, int(lifetime[:-1]), time.process_time() * 20
                    ),
                    lambda: Lifetime(
                        LifetimeType.DECIMAL_SECONDS,
                        int(lifetime[:-1]),
                        time.process_time() * 0.864,
                    ),
                ]["luts".find(lifetime[-1])]
                if lifetime[-1] in "luts"
                else exec("raise RuntimeError(f'Invalid lifetime {lifetime}')")
            )()
        )

    def visit_class_definition(self, node: ClassDefinition, env: Environment):
        parent_class = None
        members = {}
        pmembers = set()
        if node.parent:
            parent_class = env.get_variable(node.parent, line=self.lines_executed)
            if not isinstance(parent_class, ClassType):
                raise RuntimeError(f"'{node.parent}' is not a valid class.")

            members = {name: value for name, value in parent_class.members.items()}
            pmembers = parent_class.public_members

        for name, value in node.members.items():
            members[name] = value

        pmembers.update(node.public_members)

        new_class = ClassType(node.__str__(), members, pmembers)
        env.add_variable(node.__str__(), new_class, Lifetime(LifetimeType.INFINITE, 0))
        return new_class

    def visit_class_instancing(self, node: ClassInstancing, env: Environment):
        # Lookup the class in the environment
        class_type = env.get_variable(node.name, line=self.lines_executed)
        if not isinstance(class_type, ClassType):
            raise RuntimeError(f"'{node.name}' is not a valid class.")

        # Create a new instance with the class fields
        instance_members = {name: value for name, value in class_type.members.items()}

        instance_env = Environment(env)
        for name, value in instance_members.items():
            instance_env.add_variable(
                name,
                self.visit_node(value, instance_env),
                Lifetime(LifetimeType.INFINITE, 0),
            )  # TODO: Add lifetimes for class members ig.

        return ClassInstance(class_type, instance_members, instance_env)

    def visit_member_access(self, node: MemberAccess, env: Environment):
        # Lookup the instance in the environment
        instance = self.visit_node(node.obj, env)
        if not isinstance(instance, ClassInstance):
            raise RuntimeError(f"'{node.obj}' is not a valid instance.")

        # Access the field of the instance
        if node.member not in instance.members:
            raise RuntimeError(f"'{node.member}' is not a valid field of '{node.obj}'.")
        if node.member not in instance.class_type.public_members:
            raise RuntimeError(
                f"'{node.member}' is not a public field of '{node.obj}'."
            )
        return ClassMemberReference(instance, node.member)

    def visit_match(self, node: Match, env: Environment):
        expr = self.visit_node(node.expr, env)
        env.add_variable("@", expr, Lifetime(LifetimeType.INFINITE, 0))
        for case in node.cases:
            v = self.visit_node(case.condition, env)

            if v == True:
                return self.visit_node(case.expr, env)
        return self.visit_node(node.otherwise, env)

    def visit_node(self, node: ASTNode, env: Environment, imperative=False):
        if isinstance(node, Unit):
            return RuntimeUnit()
        if isinstance(node, Number):
            return RuntimeNumber(node.value)
        if isinstance(node, String):
            return RuntimeString(node.value)
        if isinstance(node, Boolean):
            return RuntimeBoolean(node.value)
        if isinstance(node, Function):
            return node
        if isinstance(node, VariableAccess):
            return env.get_variable(node.name, line=self.lines_executed)
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
        if isinstance(node, ClassDefinition):
            return self.visit_class_definition(node, env)
        if isinstance(node, ClassInstancing):
            return self.visit_class_instancing(node, env)
        if isinstance(node, MemberAccess):
            return self.visit_member_access(node, env)
        if isinstance(node, ClassMemberReference):
            return node.get()
        if isinstance(node, Match):
            return self.visit_match(node, env)
        if isinstance(node, JumpStatement):
            self.swap_file(
                self.visit_node(node.file_expr, env),
                self.visit_node(node.line_expr, env),
            )
            return Unit()
        raise NotImplementedError(f"Node {node} not implemented")

    def swap_file(self, filename: MLType, line: int):
        if isinstance(filename, RuntimeString):
            filename = filename.value
        else:
            raise RuntimeError(f"Expected string, got {filename}")

        if isinstance(line, RuntimeNumber):
            line = int(line.value)
        else:
            raise RuntimeError(f"Expected number, got {line}")

        if filename not in self.files:
            self.files[filename] = runner.fetch_file(filename)

        # print(f"Swapping to {filename} at line {line}")

        self.ast = self.files[filename]

        self.current_line = line - 1
        if self.current_line > len(self.ast):
            raise RuntimeError(f"Line {line} is out of bounds in file {filename}")

    def execute(self, ast: List[ASTNode], filename: str):
        self.ast = ast
        self.current_line = 1
        self.lines_executed = 1
        self.files[filename] = ast

        while self.current_line <= len(self.ast):
            node = self.ast[self.current_line - 1]
            try:
                self.visit_node(node, self.global_environment, imperative=True)
            except RuntimeError as e:
                print(f"Error at line {self.current_line}, {e}")
                return 1
            self.current_line += 1
            self.lines_executed += 1
        return 0
