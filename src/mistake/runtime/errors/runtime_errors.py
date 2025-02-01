class RuntimeError(Exception):
    pass


class VariableNotFoundError(RuntimeError):
    pass


class VariableAlreadyDefinedError(RuntimeError):
    pass


class InvalidAssignmentError(RuntimeError):
    pass


class InvalidFunctionCallError(RuntimeError):
    pass


class InvalidLifetimeError(RuntimeError):
    pass


class LifetimeExpiredError(RuntimeError):
    pass


class StackEmptyError(RuntimeError):
    pass


class FileSwitchException(RuntimeError):
    pass


class RuntimeTypeError(RuntimeError):
    pass
