class ParserError(Exception):
    pass
class UnexpectedTokenError(ParserError): 
    pass
class UnknownTokenError(ParserError): 
    pass
class InvalidIdentifierError(ParserError): 
    pass