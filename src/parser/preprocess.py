from tokenizer.token import Token, TokenType, opening_tokens
from typing import List


def preprocess_tokens(tokens: List[Token]):
    stack = []
    for i in tokens:
        print(stack)
        if i.type in opening_tokens:
            stack.append(i)
        elif i.type == TokenType.KW_CLOSE:
            try:
                stack.pop()
            except IndexError:
                raise Exception("Unbalanced open/close tokens")
    if len(stack) > 0:
        raise Exception("Unbalanced open/close tokens")
    return