from tokenizer.token import Token, TokenType
from typing import List


def preprocess_tokens(tokens: List[Token]):
    stack = []
    for i in tokens:
        if i.type == TokenType.KW_OPEN:
            stack.append(i)
        elif i.type == TokenType.KW_CLOSE:
            stack.pop()
    
    if len(stack) > 0:
        raise Exception("Unbalanced open/close tokens")
    
    return