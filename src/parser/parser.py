from utils import *
from typing import List, Callable, Dict
from tokenizer.token import Token, TokenType
from parser.ast import *
from parser.errors.parser_errors import *
from parser.preprocess import preprocess_tokens

class Parser:
    def __init__(self):
        self.tokens = []
        self.position = 0
        self.current_token = None
        
    def parse(self, tokens: List[Token]) -> ASTNode:
        self.tokens = tokens
        
        preprocess_tokens(self.tokens)
        
        self.position = 0
        self.current_token = self.tokens[self.position]
        
        return self.parse_program()
    
    def parse_program(self):
        nodes = []
        while self.current_token.type != TokenType.SYM_EOF:
            nodes.append(self.parse_node())
        return nodes
    
    def eat(self, token_type: TokenType):
        if self.current_token.type == token_type:
            self.position += 1
            if self.position < len(self.tokens):
                self.current_token = self.tokens[self.position]
            return self.tokens[self.position-1]
        else:
            raise UnexpectedTokenError(f"Unexpected token {self.current_token} at position {self.position}, expected {token_type}")

    
    def peek_next_is(self, token_type: TokenType):
        return self.tokens[self.position + 1].type == token_type
        
    
    def next_is(self, token_type: TokenType):
        return self.current_token.type == token_type
    

    def parse_node(self):
        if self.current_token.type == TokenType.KW_VARIABLE:
            val = self.parse_variable_declaration()
        else:
            try:
                val = self.parse_expression()
            except UnexpectedTokenError as e:
                raise e
        self.eat(TokenType.KW_END)
        return val  
    
    def advance(self):
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
    
    def parse_single_expr(self, atom: ASTNode, allow_function_application=True):
        if self.next_is(TokenType.KW_END) or self.next_is(TokenType.KW_CLOSE) or not allow_function_application:
            return atom
        
        return self.parse_function_application(atom)
        
    
    def parse_expression(self, allow_function_application=True):
        match self.current_token.type:
            case TokenType.SYM_NUMBER:
                val = Number(self.eat(TokenType.SYM_NUMBER).value)
            case TokenType.SYM_STRING:
                val =  String(self.eat(TokenType.SYM_STRING).value)
            case TokenType.KW_TRUE:
                val =  Boolean(True)
            case TokenType.KW_FALSE:
                val =  Boolean(False)
            case TokenType.SYM_IDENTIFIER:
                val =  self.parse_id_expression(allow_function_application=allow_function_application)
            case TokenType.KW_OPEN:
                val =  self.parse_block()
            case TokenType.KW_FUNCTION:
                val =  self.parse_function_declaration()
            case TokenType.KW_IMPURE:
                val =  self.parse_function_declaration()
            case _:
                raise UnexpectedTokenError(f"Unexpected token {self.current_token} at position {self.position}")
            
        return self.parse_single_expr(val, allow_function_application=allow_function_application)
    
    def parse_variable_declaration(self):
        self.eat(TokenType.KW_VARIABLE)
        name = self.eat(TokenType.SYM_IDENTIFIER).value
        if self.next_is(TokenType.KW_TYPE):
            self.eat(TokenType.KW_TYPE)
            self.advance()
        lifetime = "inf"
        if self.next_is(TokenType.KW_LIFETIME):
            self.eat(TokenType.KW_LIFETIME)
            lifetime = self.eat(TokenType.SYM_DURATION).value
            
        self.eat(TokenType.KW_IS)
        value = self.parse_expression()        
        return VariableDeclaration(name, value, lifetime)

    def parse_id_expression(self, allow_function_application=True):
        if self.tokens[self.position + 1].type not in [TokenType.KW_END, TokenType.KW_CLOSE, TokenType.SYM_EOF] and allow_function_application:
            return self.parse_function_application(VariableAccess(self.eat(TokenType.SYM_IDENTIFIER).value))

        return VariableAccess(self.eat(TokenType.SYM_IDENTIFIER).value)
    
    def get_function_application_from_params(self, expr: ASTNode, params: List[ASTNode]):
        for param in params:
            expr = FunctionApplication(expr, param)
        return expr
    
    def parse_function_application(self, func: ASTNode=None):
        parameters = []
        
        while self.current_token.type not in [TokenType.KW_END, TokenType.KW_CLOSE, TokenType.SYM_EOF]:
            parameters.append(self.parse_expression(allow_function_application=False))
        
        return self.get_function_application_from_params(func, parameters)
    
    def close_comes_before_end(self):
        for token in self.tokens[self.position:]:
            if token.type == TokenType.KW_CLOSE:
                return True
            if token.type == TokenType.KW_END:
                return False
        return False
    
    def parse_block(self):
        self.eat(TokenType.KW_OPEN)
        body = []
        while self.current_token.type != TokenType.KW_CLOSE:
            if self.close_comes_before_end():
                body.append(self.parse_expression())
            else:
                body.append(self.parse_node())
        self.eat(TokenType.KW_CLOSE)
        return Block(body)