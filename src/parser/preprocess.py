from tokenizer.token import Token, TokenType
from typing import List


def preprocess_tokens(tokens: List[Token]):
    stack = []
    in_match = False
    for i in tokens:
        if i.type == TokenType.KW_OPEN and not in_match:
            stack.append(i)
        elif i.type == TokenType.KW_CLOSE and not in_match:
            try:
                stack.pop()
            except IndexError:
                raise Exception("Unbalanced open/close tokens")
        elif i.type == TokenType.KW_MATCH:
            in_match = True
        elif i.type == TokenType.KW_END:
            if in_match: in_match = False
            
    if len(stack) > 0:
        raise Exception("Unbalanced open/close tokens")
    
    return