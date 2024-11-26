import ply.lex as lex
import ply.yacc as yacc
import os
import numpy as np

funcs = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "arcsin": np.arcsin,
    "arccos": np.arccos,
    "arctan": np.arctan,
    "sinh": np.sinh,
    "cosh": np.cosh,
    "tanh": np.tanh,
    "arcsinh": np.arcsinh,
    "arccosh": np.arccosh,
    "arctanh": np.arctanh,
    "round": np.round,
    "floor": np.floor,
    "ceil": np.ceil,
    "exp": np.exp,
    "log": np.log,
    "log10": np.log10,
    "log2": np.log2,
    "sqrt": np.sqrt,
    "cbrt": np.cbrt,
    "fabs": np.fabs,
}


class Parser:
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()

    def __init__(self, **kw):
        self.debug = kw.get('debug', 0)
        self.names = {}
        self.errors = set()
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[
                1] + "_" + self.__class__.__name__
        except:
            modname = "parser" + "_" + self.__class__.__name__
        self.debugfile = modname + ".dbg"
        # print self.debugfile

        # Build the lexer and parser
        lex.lex(module=self, debug=self.debug)
        self.parser = yacc.yacc(module=self,
                                debug=self.debug,
                                debugfile=self.debugfile)

    def run_example(self, example: str, names: dict[str, np.ndarray]):
        self.errors = set()
        self.names = names
        try:
            # yacc.parse(example)
            return self.parser.parse(example)
        except Exception as e:
            self.errors.add(e)


class Calc(Parser):

    tokens = (
        'NAME', 'INTEGER', 'FLOAT',
        'PLUS', 'MINUS', 'EXP', 'TIMES', 'DIVIDE', 'INT_DIV', 'MODULO',
        'EQUALS', 'NOT_EQUALS', 'LESS', 'GREATER', 'LESS_EQUALS', 'GREATER_EQUALS',
        'NOT', 'AND', 'OR', 'XOR', 'LEFT_SHIFT', 'RIGHT_SHIFT',
        'LPAREN', 'RPAREN',
    )

    # Tokens

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_EXP = r'\*\*'
    t_TIMES = r'\*'
    t_INT_DIV = r'//'
    t_DIVIDE = r'/'
    t_MODULO = r'%'
    t_EQUALS = r'=='
    t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    t_NOT_EQUALS = r'!='
    t_NOT = r'~'
    t_LESS_EQUALS = r'<='
    t_GREATER_EQUALS = r'>='
    t_LESS = r'<'
    t_GREATER = r'>'
    t_AND = r'&'
    t_OR = r'\|'
    t_XOR = r'\^'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LEFT_SHIFT = r'<<'
    t_RIGHT_SHIFT = r'>>'

    def t_FLOAT(self, t):
        r'(\d*\.\d+)|(\d+\.\d*)'
        try:
            t.value = float(t.value)
        except ValueError:
            self.errors.add("invalid float value %s" % t.value)
            t.value = 0.0
        return t

    def t_INTEGER(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            self.errors.add("invalid integer value %s" % t.value)
            t.value = 0
        return t

    t_ignore = " \t"

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        self.errors.add("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Parsing rules

    precedence = (
        ('left', 'EQUALS', 'NOT_EQUALS', 'LESS', 'GREATER', 'LESS_EQUALS', 'GREATER_EQUALS'),
        ('left', 'OR'),
        ('left', 'XOR'),
        ('left', 'AND'),
        ('left', 'LEFT_SHIFT', 'RIGHT_SHIFT'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'INT_DIV', 'MODULO'),
        ('left', 'EXP'),
        ('right', 'UMINUS', 'UNOT'),
    )

    def p_statement_expr(self, p):
        'statement : expression'
        p[1]

    def p_expression_binop(self, p):
        """
        expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression INT_DIV expression
                  | expression EXP expression
                  | expression MODULO expression
                  | expression EQUALS expression
                  | expression NOT_EQUALS expression
                  | expression LESS expression
                  | expression GREATER expression
                  | expression LESS_EQUALS expression
                  | expression GREATER_EQUALS expression
                  | expression LEFT_SHIFT expression
                  | expression RIGHT_SHIFT expression
                  | expression AND expression
                  | expression XOR expression
                  | expression OR expression
        """
        if p[2] == '+':
            p[0] = p[1] + p[3]
        elif p[2] == '-':
            p[0] = p[1] - p[3]
        elif p[2] == '*':
            p[0] = p[1] * p[3]
        elif p[2] == '/':
            p[0] = p[1] / p[3]
        elif p[2] == '**':
            p[0] = p[1] ** p[3]
        elif p[2] == '//':
            p[0] = p[1] // p[3]
        elif p[2] == '%':
            p[0] = p[1] % p[3]
        elif p[2] == '==':
            p[0] = p[1] == p[3]
        elif p[2] == '!=':
            p[0] = p[1] != p[3]
        elif p[2] == '<':
            p[0] = p[1] < p[3]
        elif p[2] == '>':
            p[0] = p[1] > p[3]
        elif p[2] == '<=':
            p[0] = p[1] <= p[3]
        elif p[2] == '>=':
            p[0] = p[1] >= p[3]
        elif p[2] == '<<':
            p[0] = p[1] << p[3]
        elif p[2] == '>>':
            p[0] = p[1] >> p[3]
        elif p[2] == '&':
            p[0] = p[1] & p[3]
        elif p[2] == '^':
            p[0] = p[1] ^ p[3]
        elif p[2] == '|':
            p[0] = p[1] | p[3]

    def p_expression_uminus(self, p):
        'expression : MINUS expression %prec UMINUS'
        p[0] = -p[2]

    def p_expression_unot(self, p):
        'expression : NOT expression %prec UNOT'
        p[0] = ~p[2]

    def p_expression_group(self, p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]

    def p_expression_number(self, p):
        '''expression : FLOAT
                     | INTEGER
        '''
        p[0] = p[1]

    def p_expression_func(self, p):
        'expression : NAME LPAREN expression RPAREN'
        try:
            if p[1] in funcs.keys():
                p[0] = funcs[p[1]](p[3])
            else:
                self.errors.add("Illegal function '%s'" % p[1])
                p[0] = 0
        except Exception as e:
            self.errors.add(e)
            p[0] = 0


    def p_expression_name(self, p):
        'expression : NAME'
        try:
            p[0] = self.names[p[1]]
        except LookupError:
            self.errors.add("Undefined name '%s'" % p[1])
            p[0] = 0

    def p_error(self, p):
        if p:
            self.errors.add("Syntax error at '%s'" % p.value)
        else:
            self.errors.add("Syntax error at EOF")


if __name__ == '__main__':
    calc = Calc()
    names = {
        'a': np.array(range(10)) - 5  #+ np.random.random(10)
    }
    # print(names['a'])
    # calc.run_example("(1 + 2) * a % 8", names)
    # print(names['a'])
    # calc.run_example("((a <= 2) & (a >= -2))", names)
    # print(calc.errors)
    # calc.run_example("~((a <= 2) & (a >= -2))", names)
    # print(calc.errors)
    # calc.run_example("-~((a <= 2) & (a >= -2))", names)
    # print(calc.errors)
    # x = calc.run_example("~((a <= b) & (a >= -2))", names)
    # print(f"{x=}")
    # print(calc.errors)
    # calc.run_example("a ", names)
    # calc.run_example("sin(a)", names)
    # print(calc.errors)
    # print(names['a'])
    # calc.run_example("arcsin(a)", names)
    # print(calc.errors)
