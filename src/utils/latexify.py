from sympy import latex, Symbol, Function
from sympy.parsing.sympy_parser import parse_expr
from utils.parser import funcs

for f_ in list(funcs.keys()):
    exec(f"{f_} = Function('{f_}')")

for f_ in range(10):
    exec(f"f_{f_} = Function('f_{f_}')")

def py_to_latex(formula: str, variables: list[str]) -> str:
    for i_ in variables:
        exec(f"{i_} = Symbol('{i_}')")
    return latex(parse_expr(formula, evaluate=False))

