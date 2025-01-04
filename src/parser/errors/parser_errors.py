class ParserError(Exception): pass
class UnexpectedTokenError(ParserError): pass
class UnknownTokenError(ParserError): pass
class UnexpectedEOFError(ParserError): pass