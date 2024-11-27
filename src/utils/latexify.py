from sympy import latex, symbols

def py_to_latex(formula: str, variables: list[str]) -> str:
    symbols_ = {x: symbols(x) for x in variables}
    return latex()

