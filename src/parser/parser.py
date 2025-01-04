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
    
    def peek_is(self, mayhaps: TokenType) -> bool:  
        return self.peek().type == mayhaps
    
    def parse(self, tokens: List[Token]) -> List[ASTNode]:
        self.tokens = tokens
        while not self.peek_is(TokenType.SYM_EOF):
            self.ast.append(self.parse_statement())
            print(self.ast)
        return self.ast
    
    def parse_statement(self, require_end=True) -> ASTNode:
        m = None
        if self.peek_is(TokenType.KW_VARIABLE):
            m = self.parse_variable_declaration()
        else:
            m = self.parse_expression()
        if require_end: self.eat(TokenType.KW_END)
        return m
        
    def parse_variable_declaration(self) -> ASTNode:
        # variable grammar = 'variable' identifier 'is' expression 'end'
        self.eat(TokenType.KW_VARIABLE)
        id = self.eat(TokenType.SYM_IDENTIFIER)
        self.eat(TokenType.KW_IS)
        expr = self.parse_expression()
        return ASTNode(NodeType.S_VARIABLE_DECLARATION, id.value, [expr])
    
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
    
    def parse_expression(self) -> ASTNode|None:
        print("EXPR", self.cur(), self.peek(), self.position)
        if self.peek_is(TokenType.KW_END) or self.peek_is(TokenType.KW_CLOSE):
            return None
        if self.peek_is(TokenType.SYM_STRING):
            self.eat(TokenType.SYM_STRING)
            return ASTNode(NodeType.E_STRING, self.eat(TokenType.SYM_STRING).value, [self.parse_expression()])
        if self.peek_is(TokenType.SYM_NUMBER):
            return ASTNode(NodeType.E_NUMBER, self.eat(TokenType.SYM_NUMBER).value, [self.parse_expression()])
        if self.peek_is(TokenType.SYM_IDENTIFIER):
            return ASTNode(NodeType.S_FUNCTION_CALL, self.eat(TokenType.SYM_IDENTIFIER).value, [self.parse_expression()])
        if self.peek_is(TokenType.KW_OPEN):
            block = self.parse_block()
            block.add_child(self.parse_expression())
            return block
        raise UnknownTokenError(f"Unknown token {self.peek()}")
        