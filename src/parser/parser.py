from utils import *
from typing import List
from tokenizer.token import Token, TokenType
from parser.ast import ASTNode, NodeType
from parser.errors.parser_errors import *
class Parser:
    def __init__(self):
        self.tokens: List[Token] = []
        self.ast: List[ASTNode] = []
        self.position = -1

    def peek(self, dist: int = 1) -> Token:
        return self.tokens[self.position + dist]
    
    def cur(self) -> Token:
        return self.tokens[self.position]
    
    def cur_is(self, mayhaps: TokenType) -> bool:
        return self.cur().type == mayhaps
    
    def advance(self) -> Token:
        self.position += 1
        return self.cur()
    
    def eat(self, expect: TokenType)  -> Token|UnexpectedTokenError:
        if self.peek().type != expect:
            raise UnexpectedTokenError(f"Expected {expect} but got {self.peek()}")
        return self.advance()
    
    def peek_is(self, mayhaps: TokenType, dist: int=1) -> bool:  
        return self.peek(dist=dist).type == mayhaps
    
    def is_valid_identifier(self, id: str, in_type: NodeType) -> bool:
        if id == "_" and in_type != NodeType.S_VARIABLE_DECLARATION:
            return False
        
        # Assume other cases would be caught by the lexer
        return True
    def parse(self, tokens: List[Token]) -> List[ASTNode]:
        self.tokens = tokens
        while not self.peek_is(TokenType.SYM_EOF):
            self.ast.append(self.parse_statement())
            print(self.ast)
        return self.ast
    
    def parse_statement(self, require_end=True) -> ASTNode:
        m = None
        if self.peek_is(TokenType.KW_VARIABLE) or (self.peek_is(TokenType.KW_PUBLIC) and self.peek_is(TokenType.KW_VARIABLE, dist=2)):
            m = self.parse_variable_declaration()
        else:
            m = self.parse_expression()
        if require_end: self.eat(TokenType.KW_END)
        return m
        
    def parse_variable_declaration(self) -> ASTNode:
        # variable grammar = 'variable' identifier 'is' expression 'end'
        is_pub = self.peek_is(TokenType.KW_PUBLIC)
        if is_pub: self.eat(TokenType.KW_PUBLIC)
        self.eat(TokenType.KW_VARIABLE)
        id = self.eat(TokenType.SYM_IDENTIFIER)
        lt: Token = None
        if self.peek_is(TokenType.KW_LIFETIME):
            self.eat(TokenType.KW_LIFETIME)
            lt = self.eat(TokenType.SYM_DURATION)
        self.eat(TokenType.KW_IS)
        expr = self.parse_expression()
        return ASTNode(NodeType.S_VARIABLE_DECLARATION, id.value, [is_pub, expr, lt] if lt else [expr])
    
    def parse_block(self) -> ASTNode:
        # block grammar = 'open' statement* 'close'
        self.eat(TokenType.KW_OPEN)
        block = ASTNode(NodeType.E_BLOCK, "block")
        while not self.peek_is(TokenType.KW_CLOSE):
            block.add_child(self.parse_statement(require_end=False))
            print(block)
            if not self.peek_is(TokenType.KW_CLOSE):
                self.eat(TokenType.KW_END)
        self.eat(TokenType.KW_CLOSE)
        return block
    
    def parse_function_declaration(self) -> ASTNode:
        # [impure] function [<identifier>]... returns <expression> close
        impure = self.peek_is(TokenType.KW_IMPURE)
        if impure: self.eat(TokenType.KW_IMPURE)
        self.eat(TokenType.KW_FUNCTION)
        ids = []
        while self.peek_is(TokenType.SYM_IDENTIFIER):
            ids.append(self.eat(TokenType.SYM_IDENTIFIER).value)
        self.eat(TokenType.KW_RETURNS)
        expr = self.parse_expression()
        self.eat(TokenType.KW_CLOSE)
        return ASTNode(NodeType.E_FUNCTION_DECLARATION, ids, [impure, expr])
    
    def parse_expression(self) -> ASTNode|None:
        print("EXPR", self.cur(), self.peek(), self.position)
        if self.peek_is(TokenType.KW_END) or self.peek_is(TokenType.KW_CLOSE):
            return None
        if self.peek_is(TokenType.SYM_STRING):
            self.eat(TokenType.SYM_STRING)
            return ASTNode(NodeType.E_STRING, self.eat(TokenType.SYM_STRING).value, [self.parse_expression()])
        if self.peek_is(TokenType.SYM_NUMBER):
            return ASTNode(NodeType.E_NUMBER, self.eat(TokenType.SYM_NUMBER).value, [self.parse_expression()])
        if self.peek_is(TokenType.SYM_IDENTIFIER) or self.peek_is(TokenType.KW_RANDOMIZE):
            if not self.is_valid_identifier(self.peek().value, NodeType.S_FUNCTION_CALL):
                raise InvalidIdentifierError(f"Invalid identifier '{self.peek().value}'")
            return ASTNode(NodeType.S_FUNCTION_CALL, self.advance().value, [self.parse_expression()])
        if self.peek_is(TokenType.KW_FUNCTION) or (self.peek_is(TokenType.KW_IMPURE) and self.peek_is(TokenType.KW_FUNCTION, dist=2)):
            return self.parse_function_declaration()
        if self.peek_is(TokenType.KW_OPEN):
            block = self.parse_block()
            block.add_child(self.parse_expression())
            return block
        raise UnknownTokenError(f"Unknown token {self.peek()}")
        
        
        