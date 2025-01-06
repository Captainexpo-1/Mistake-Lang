from tokenizer.token import Token, TokenType
from typing import List


def preprocess_tokens(tokens: List[Token]):
    stack = []
    exceptions = set()
    for i in tokens:
        print(exceptions)
        if i.type == TokenType.KW_OPEN:
            stack.append(i)
        elif i.type == TokenType.KW_CLOSE:
            if TokenType.SYM_STRING in exceptions:
                exceptions.remove(TokenType.SYM_STRING)
                continue
            try:
                stack.pop()
            except IndexError:
                raise Exception("Unbalanced open/close tokens")
        elif i.type == TokenType.KW_MATCH:
            exceptions.add(TokenType.KW_MATCH)
        elif i.type == TokenType.SYM_STRING:
            exceptions.add(TokenType.SYM_STRING)
        elif i.type == TokenType.KW_END:
            if TokenType.KW_MATCH in exceptions:
                exceptions.remove(TokenType.KW_MATCH)
                continue
            
            
    if len(stack) > 0:
        raise Exception("Unbalanced open/close tokens")
    
    return