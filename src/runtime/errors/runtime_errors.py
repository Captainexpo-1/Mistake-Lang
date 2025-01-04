class RuntimeError(Exception): pass
class UndefinedVariableError(RuntimeError): pass
class InvalidAssignmentError(RuntimeError): pass
class InvalidFunctionCallError(RuntimeError): pass

class InvalidLifetimeError(RuntimeError): pass