from strings_with_arrows import string_with_arrows
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
        result = f'ERROR {self.error_name}: {self.details}\n'
        result += f'  File {self.pos_start.fn}, line {self.pos_start.ln + 1}\n'
        result += '\n' + string_with_arrows(self.pos_start.ftxt,
                                            self.pos_start, self.pos_end)
        return result


class IllegalCharError(Error):

    def __init__(self, pos_start, pos_end, details='') -> None:
        super().__init__(pos_start, pos_end, 'Illegal Character', details)


class InvalidSyntaxError(Error):

    def __init__(self, pos_start, pos_end, details='') -> None:
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)


## POSITION


class Position:

    def __init__(self, idx, ln, col, fn, ftxt) -> None:
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_chr=None):
        self.idx += 1
        self.col += 1

        if current_chr == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)


## TOKENS

TT_INT: Final = 'INT'
TT_FLOAT: Final = 'FLOAT'
TT_PLUS: Final = 'PLUS'
TT_MINUS: Final = 'MINUS'
TT_MUL: Final = 'MUL'
TT_DIV: Final = 'DIV'
TT_LPAREN: Final = 'LPAREN'
TT_RPAREN: Final = 'RPAREN'
TT_EOF: Final = 'EOF'


class Token:

    def __init__(self,
                 type_,
                 value=None,
                 pos_start=None,
                 pos_end=None) -> None:
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end.copy()

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
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_chr == '-':
                tokens.append(Token(TT_MINUS, pos_start=self.pos))
                self.advance()
            elif self.current_chr == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_chr == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_chr == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_chr == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_chr
                self.advance()
                return [], IllegalCharError(pos_start, self.pos,
                                            "'" + char + "'")
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0

        pos_start = self.pos.copy()

        while self.current_chr != None and self.current_chr in DIGITS + '.':
            if self.current_chr == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_chr

            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, pos_end=self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, pos_end=self.pos)


## NODES


class NumberNode:

    def __init__(self, tok) -> None:
        self.tok = tok

    def __repr__(self) -> str:
        return f'{self.tok}'


class BinOpNode:

    def __init__(self, left_node, op_tok, right_node) -> None:
        self.left_node = left_node
        self.right_node = right_node
        self.op_tok = op_tok

    def __repr__(self) -> str:
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'


class UnaryOpNode:

    def __init__(self, op_tok, node) -> None:
        self.op_tok = op_tok
        self.node = node

    def __repr__(self) -> str:
        return f'({self.op_tok}, {self.node})'


## PARSE RESULT


class ParseResult:

    def __init__(self) -> None:
        self.error = None
        self.node = None

    def regisrer(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node

        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self


## PARSER


class Parser:

    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(
                InvalidSyntaxError(self.current_tok.pos_start,
                                   self.current_tok.pos_end,
                                   "Expected '+', '-', '*' or '/'"))
        return res

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.regisrer(self.advance())
            factor = res.regisrer(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        elif tok.type in (TT_INT, TT_FLOAT):
            res.regisrer(self.advance())
            return res.success(NumberNode(tok))

        elif tok.type == TT_LPAREN:
            res.regisrer(self.advance())
            expr = res.regisrer(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.regisrer(self.advance())
                return res.success(expr)
            else:
                return res.failure(
                    InvalidSyntaxError(self.current_tok.pos_start,
                                       self.current_tok.pos_end,
                                       "Expected ')'"))

        return res.failure(
            InvalidSyntaxError(tok.pos_start, tok.pos_end,
                               'Expected int or float'))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.regisrer(func())
        if res.error: return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.regisrer(self.advance())
            right = res.regisrer(func())

            if res.error: return res

            left = BinOpNode(left, op_tok, right)

        return res.success(left)


## RUN


def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    parser = Parser(tokens)
    ast = parser.parse()

    return ast.node, ast.error
