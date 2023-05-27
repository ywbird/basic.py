from typing import Final, List

## CONSTANTS

DIGITS: Final = '012345679'

## ERROR


class Error:

    def __init__(self, pos_start, pos_end, error_name, details) -> None:
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self) -> str:
        result = f'ERROR {self.error_name}:\n'
        result += f'  File {self.pos_start.fn}, line {self.pos_start.ln + 1}\n'
        result += f'    {self.details}'
        return result


class IllegalCharError(Error):

    def __init__(self, pos_start, pos_end, details) -> None:
        super().__init__(pos_start, pos_end, 'Illegal Character', details)


## POSITION


class Position:

    def __init__(self, idx, ln, col, fn, ftxt) -> None:
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_chr):
        self.idx += 1
        self.col += 1

        if current_chr == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


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

    def __init__(self, fn, text) -> None:
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, self.fn, text)
        self.current_chr = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_chr)
        self.current_chr = self.text[self.pos.idx] if self.pos.idx < len(
            self.text) else None

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
                pos_start = self.pos.copy()
                char = self.current_chr
                self.advance()
                return [], IllegalCharError(pos_start, self.pos,
                                            "'" + char + "'")

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


def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()

    return tokens, error
