from mistake.runtime.runtime_types import MLType, Lifetime

from mistake.runtime.errors.runtime_errors import LifetimeExpiredError, VariableNotFoundError, VariableAlreadyDefinedError

from mistake.runtime.stdlib import std_funcs as stdlib

class ContextType:
    PURE = 0
    IMPURE = 1

class Environment:
    def __init__(self, parent: "Environment", context_type: ContextType = ContextType.IMPURE):
        self.variables: dict[str, MLType] = {}
        self.lifetimes: dict[str, Lifetime] = {}
        self.parent = parent
        self.context_type = context_type

    def get_variable(self, name: str, line: int = 0) -> MLType:
        if name in self.variables:
            if self.lifetimes[name].is_expired(line):
                del self.variables[name]
                del self.lifetimes[name]
                raise LifetimeExpiredError(f"Lifetime for variable {name} has expired")
            return self.variables[name]

        if self.parent and self.context_type == ContextType.IMPURE:
            return self.parent.get_variable(name)

        if name in stdlib.std_funcs:
            return stdlib.std_funcs[name]

        raise VariableNotFoundError(f"Variable {name} not found.")

    def add_variable(self, name: str, value: MLType, lifetime: Lifetime, ignore_duplicate=False):
        if name == "_": return
        if not ignore_duplicate and name in self.variables:
            raise VariableAlreadyDefinedError(
                f"Variable {name} already defined in this scope"
            )

        self.variables[name] = value

        if not isinstance(lifetime, Lifetime):
            raise TypeError(f"{lifetime} must be of type Lifetime")
        self.lifetimes[name] = lifetime

    def absorb_environment(self, env: "Environment"):
        for var in env.variables:
            self.add_variable(var, env.get_variable(var), env.lifetimes[var], ignore_duplicate=True)

    def __repr__(self):
        out = "Environment((\n"
        for var in self.variables:
            out += f"   {var}: {self.variables[var].to_string()}\n"

        out += f"), {self.context_type})"
        return out

