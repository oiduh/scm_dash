from sympy import latex, Symbol, Function
from utils.parser import funcs

for f_ in list(funcs.keys()):
    exec(f"{f_} = Function('{f_}')")


def py_to_latex(formula: str, variables: list[str]) -> str:
    for i_ in variables:
        exec(f"{i_} = Symbol('{i_}')")
    return latex(eval(formula))

