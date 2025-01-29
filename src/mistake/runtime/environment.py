import time

from mistake.runtime.errors.runtime_errors import (
    LifetimeExpiredError,
    VariableAlreadyDefinedError,
    VariableNotFoundError,
)
from mistake.runtime.runtime_types import Lifetime, MLType
from mistake.runtime.stdlib import std_funcs as stdlib


class ContextType:
    PURE = 0
    IMPURE = 1


test = []


class Environment:
    def __init__(
        self, parent: "Environment", context_type: ContextType = ContextType.IMPURE
    ):
        self.variables: dict[str, MLType] = {}
        self.lifetimes: dict[str, Lifetime] = {}
        self.parent = parent
        self.context_type = context_type
        self.test_time = time.process_time_ns()
        test.append(self)

    def get_variable(self, name: str, line: int = 0) -> MLType:
        if name in self.variables:
            if self.lifetimes[name].is_expired(line):
                del self.variables[name]
                del self.lifetimes[name]
                raise LifetimeExpiredError(f"Lifetime for variable {name} has expired")
            return self.variables[name]

        if self.parent:  # and self.context_type == ContextType.IMPURE:
            return self.parent.get_variable(name)

        if name in stdlib.std_funcs:
            return stdlib.std_funcs[name]

        raise VariableNotFoundError(f"Variable {name} not found.")

    def get_full_var_data(self, name: str):
        if name in self.variables:
            return self.variables[name], self.lifetimes[name]
        if self.parent:
            return self.parent.get_full_var_data(name)
        raise VariableNotFoundError(f"Variable {name} not found.")

    def add_variable(
        self, name: str, value: MLType, lifetime: Lifetime, ignore_duplicate=False
    ):
        if name == "_":
            return

        if not ignore_duplicate and name in self.variables:
            raise VariableAlreadyDefinedError(
                f"Variable {name} already defined in this scope"
            )

        self.variables[name] = value

        if not isinstance(lifetime, Lifetime):
            raise TypeError(f"{lifetime} must be of type Lifetime")
        self.lifetimes[name] = lifetime

    def get_all_defined_vars(self):
        vars = []
        for var in self.variables:
            vars.append(var)
        if self.parent:
            vars.extend(self.parent.get_all_defined_vars())
        return vars

    def absorb_environment(self, env: "Environment"):
        for var in env.variables:
            self.add_variable(
                var, env.get_variable(var), env.lifetimes[var], ignore_duplicate=True
            )

    def repr_simple(self):
        return f"{str(id(self))[-4:]}({','.join(self.get_all_defined_vars())})({self.test_time})"

    def __repr__(self):
        out = f"Environment({id(self)}, (\n"
        for var in self.variables:
            out += f"   {var}: {self.variables[var].to_string()}\n"

        out += f"), {self.context_type}, {id(self.parent)})"
        return out
