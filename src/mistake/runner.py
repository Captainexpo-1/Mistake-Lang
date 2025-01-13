def fetch_file(filename: str):
    return (
        __import__("parser.parser")
        .parser.Parser()
        .parse(
            __import__("tokenizer.lexer").lexer.Lexer().tokenize(open(filename).read())
        )
    )
