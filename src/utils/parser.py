import ply.lex as lex
import ply.yacc as yacc
import os


class Parser:
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()

    def __init__(self, **kw):
        self.debug = kw.get('debug', 0)
        self.names = {}
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[
                1] + "_" + self.__class__.__name__
        except:
            modname = "parser" + "_" + self.__class__.__name__
        self.debugfile = modname + ".dbg"
        # print self.debugfile

        # Build the lexer and parser
        lex.lex(module=self, debug=self.debug)
        yacc.yacc(module=self,
                  debug=self.debug,
                  debugfile=self.debugfile)

    def run(self):
        while True:
            try:
                s = input('calc > ')
            except EOFError:
                break
            if not s:
                continue
            yacc.parse(s)

    def run_example(self, example: str):
        yacc.parse(example)


class Calc(Parser):

    tokens = (
        'NAME', 'NUMBER',
        'PLUS', 'MINUS', 'EXP', 'TIMES', 'DIVIDE', 'EQUALS', 'NOT_EQUALS', 'INT_DIV',
        'LESS', 'GREATER', 'LESS_EQUAL', 'GREATER_EQUAL', 'NOT', 'AND', 'OR', 'XOR',
        'LPAREN', 'RPAREN',
    )

    # Tokens

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_EXP = r'\*\*'
    t_TIMES = r'\*'
    t_INT_DIV = r'//'
    t_DIVIDE = r'/'
    t_EQUALS = r'='
    t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    t_NOTEQUALS = r'!='
    t_NOT = r'~'
    t_LESS_EQUAL = r'<='
    t_GREATER_EQUAL = r'>='
    t_LESS = r'<'
    t_GREATER = r'>'
    t_AND = r'&'
    t_OR = r'|'
    t_XOR = r'^'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'

    def t_NUMBER(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            print("Integer value too large %s" % t.value)
            t.value = 0
        # print "parsed number %s" % repr(t.value)
        return t

    t_ignore = " \t"

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Parsing rules

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('left', 'EXP'),
        ('right', 'UMINUS', 'UNOT'),
    )

    def p_statement_assign(self, p):
        'statement : NAME EQUALS expression'
        self.names[p[1]] = p[3]

    def p_statement_expr(self, p):
        'statement : expression'
        print(p[1])

    def p_expression_binop(self, p):
        """
        expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression EXP expression
        """
        # print [repr(p[i]) for i in range(0,4)]
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
        'expression : NUMBER'
        p[0] = p[1]

    def p_expression_name(self, p):
        'expression : NAME'
        try:
            p[0] = self.names[p[1]]
        except LookupError:
            print("Undefined name '%s'" % p[1])
            p[0] = 0

    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")


if __name__ == '__main__':
    calc = Calc()
    # calc.run()
    calc.run_example("(1 + 2) * a")
