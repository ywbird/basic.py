from typing import Final, List

## CONSTANTS

DIGITS: Final = '012345679'

## ERROR


class Error:

    def __init__(self, error_name, details) -> None:
        self.error_name = error_name
        self.details = details

    def as_string(self) -> str:
        result = f'{self.error_name}: {self.details}'
        return result


class IllegalCharError(Error):

    def __init__(self, details) -> None:
        super().__init__('Illegal Character', details)


## TOKENS

TT_INT: Final = 'TT_INT'
TT_FLOAT: Final = 'FLOAT'
TT_PLUS: Final = 'PLUS'
TT_MINUS: Final = 'MINUS'
TT_MUL: Final = 'MUL'
TT_DIV: Final = 'DIV'
TT_LPAREN: Final = 'LPAREN'
TT_RPAREN: Final = 'RPAREN'


class Token:

    def __init__(self, type_, value=None) -> None:
        self.type = type_
        self.value = value

    def __repr__(self) -> str:
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'


## LEXER


class Lexer:

    def __init__(self, text) -> None:
        self.text = text
        self.pos = -1
        self.current_chr = None
        self.advance()

    def advance(self):
        self.pos += 1
        self.current_chr = self.text[self.pos] if self.pos < len(
            self.text) else None
        self.next_chr = ''
        if self.pos + 1 < len(self.text):
            self.next_chr = self.text[self.pos + 1]
        else:
            self.next_chr = None

    def make_tokens(self) -> List[str]:
        tokens: List[str] = []

        while self.current_chr != None:
            if self.current_chr in ' \t':
                self.advance()
            elif self.current_chr in DIGITS:
                tokens.append(self.make_number())
            elif self.current_chr == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_chr == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_chr == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_chr == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_chr == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_chr == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            else:
                char = self.current_chr
                self.advance()
                return [], IllegalCharError("'" + char + "'")

        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.current_chr != None and self.current_chr in DIGITS + '.':
            if self.current_chr == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_chr

            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))


## RUN


def run(text):
    lexer = Lexer(text)
    tokens, error = lexer.make_tokens()

    return tokens, error
