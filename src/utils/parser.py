from enum import StrEnum
import string


"""
very simple parser for mathematical equations for the mechanism
parser only used for verifaction of input and extration of variables and 'builtin' functions
"""

class Symbols(StrEnum):
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    MODULO = "MODULO"
    EXPONENT = "EXPONENT"
    FLOOR_DIVIDE = "FLOOR_DIVIDE"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS = "LESS"
    GREATER = "GREATER"
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    AND = "AND"
    OR = "OR"
    XOR = "XOR"
    NOT = "NOT"


SYMBOL_MAP = {
    "(" : Symbols.LPAREN,
    ")" : Symbols.RPAREN,
    "+" : Symbols.PLUS,
    "-" : Symbols.MINUS,
    "*" : Symbols.MULTIPLY,
    "**" : Symbols.EXPONENT,
    "/" : Symbols.DIVIDE,
    "//" : Symbols.FLOOR_DIVIDE,
    "%" : Symbols.MODULO,
    "<=" : Symbols.LESS_EQUAL,
    ">=" : Symbols.GREATER_EQUAL,
    "<" : Symbols.LESS,
    ">" : Symbols.GREATER,
    "=" : Symbols.EQUAL,
    "!=" : Symbols.NOT_EQUAL,
    "&" : Symbols.AND,
    "|" : Symbols.OR,
    "^" : Symbols.XOR,
    "!" : Symbols.NOT,
}


class TokenType(StrEnum):
    SYMBOL = "SYMBOL"
    ID = "ID"
    NUMBER = "NUMBER"
    INVALID_SYMBOL = "INVALID_SYMBOL"
    INVALID_NUMBER = "INVALID_NUMBER"


class Token:
    def __init__(self, token_type: TokenType, value: str) -> None:
        self.id = token_type
        self.value = value

    def __str__(self) -> str:
        return f"({self.id}, {self.value})"

    def __repr__(self) -> str:
        return self.__str__()


def tokenize(input: str) -> list[Token]:

    tokens: list[Token] = []
    idx = 0
    while idx < len(input):
        char = input[idx]
        if char in string.whitespace:
            idx += 1
            continue
        if idx < len(input) - 1 and (m:=input[idx:idx+2]) in SYMBOL_MAP:
            # print(TOKEN_MAP[m], end="")
            idx += 2
            tokens.append(Token(TokenType.SYMBOL, SYMBOL_MAP[m]))
        elif char in SYMBOL_MAP:
            # print(TOKEN_MAP[char], end="")
            idx += 1
            tokens.append(Token(TokenType.SYMBOL, SYMBOL_MAP[char]))
        elif char.isdigit() or char == ".":
            num_str = [char]
            skip = idx + 1
            while skip < len(input) and (next:=input[skip]) and (next.isdigit() or next == "."):
                num_str.append(next)
                skip += 1
            idx = skip
            num_str = "".join(num_str)
            try:
                num = float(num_str)
                # print(f"<NUM: '{num}'>", end="")
                tokens.append(Token(TokenType.NUMBER, str(num)))
            except Exception:
                # print("<INVALID_NUMBER>", end="")
                tokens.append(Token(TokenType.INVALID_NUMBER, num_str))
        elif char in string.ascii_letters or char == "_":
            name = [char]
            skip = idx + 1
            while skip < len(input) and (next:=input[skip]) and (next in string.ascii_letters or next == "_"):
                name.append(next)
                skip += 1
            idx = skip
            name = "".join(name)
            # print(f"<VAR: '{name}'>", end="")
            tokens.append(Token(TokenType.ID, name))
        else:
            # print(f"<INVALID_CHAR: '{char}'>", end="")
            idx += 1
            tokens.append(Token(TokenType.INVALID_SYMBOL, char))

    return tokens


def parse(tokens: list[Token]) -> bool:
    return False


if __name__ == "__main__":
    x = tokenize("0.0 + a + sin(a b) !")
    y = parse(x)
    print(x)

