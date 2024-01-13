from ast import BinOp, Call, Constant, Load, Name
from dash import MATCH, Input, Output, callback, html, State, ctx
from dash.exceptions import PreventUpdate
from graph_builder import graph_builder_component
from dash.dcc import Input as InputField
from typing import Any, List, Dict
import numpy as np
from enum import Enum
import ast
import numpy as np
from numpy.typing import NDArray

# trignometry
sin = np.sin
cos = np.cos
tan = np.tan
arcsin = np.arcsin
arccos = np.arccos
arctan = np.arctan
arctan2 = np.arctan2

# hyperbolic
sinh = np.sinh
cosh = np.cosh
tanh = np.tanh
arcsinh = np.arcsinh
arccosh = np.arccosh
arctanh = np.arctanh

# rounding
round = np.round
floor = np.floor
ceil = np.ceil

# exponents and logarithms
exp = np.exp
log = np.log
log10 = np.log10
log2 = np.log2

# misc
sqrt = np.sqrt
clip = np.clip
cbrt = np.cbrt
fabs = np.fabs



# mechanism builder plan:
#   2 types:
#     classification -> fixed amount of output values
#     regression -> continuous output values
#   inputs:
#     each node has at least 1 input (noise)
#     the output is a combination of all inputs -> some mechanism
#   mechansims:
#     classification -> at least 2 classes -> add more dynamically
#     regression -> should be simple

# regression:
#   we get 1 input string (formula) and use it to transform all node data
#   to some output data -> 'x + y + z = w'

# classification:
#   we get multiple input formulas (number of formulas = number of classes)
#   each formula must evaluate to a bool -> belongs to class or does not
#   for each formula only 1 can evaluate to true for a data entry
#   incomplete classification e.g. not handling all data entries -> create
#     on dummy class which is displayed if at least on entry


class BaseMechanism:
    def __init__(self, inputs: Dict[str, np.ndarray]):
        self.inputs = inputs

    def transform(self):
        raise NotImplemented


class ClassificationMechanism(BaseMechanism):
    def __init__(self, inputs: Dict[str, np.ndarray]):
        super().__init__(inputs)

    def transform(self, formulas: list[str]):
        results = np.full((len(formulas), len(list(self.inputs.values())[0])), False)

        failed = False
        for idx, formula in enumerate(formulas):
            tree = ast.parse(formula)
            for a in ast.walk(tree):
                if isinstance(a, Name) and a.id in self.inputs.keys():
                    a.id = f"self.inputs[\"{a.id}\"]"
            new_formula = ast.unparse(tree)
            try:
                result: NDArray[Any] = eval(new_formula)
                assert result.dtype == bool, "NOT A BOOL"
                results[idx] = result
            except Exception as e:
                failed = True
                print(e)
        if failed:
            raise Exception("one of the formulas does not produce booleans")

        if np.any(np.sum(results, axis=0) > 1.0):
            raise Exception("value belongs to more than one class")

        # TODO: check all columns -> if one has no True value add new row,
        #       where all False column become True -> undefined class
        #       somehow mark empty classes
        results = np.vstack([results, np.full(len(list(self.inputs.values())[0]), False)])
        for idx, col in enumerate(np.sum(results, axis=0)):
            if col == 0:
                results[-1][idx] = True

        if not np.any(results[-1]):
            results = results[:-1]

        if np.prod(np.sum(results, axis=0)) != 1.:
            raise Exception("a data entry must belong to exactly one class")

        return results


class RegressionMechanism(BaseMechanism):
    def __init__(self, inputs: Dict[str, np.ndarray]):
        super().__init__(inputs)

    def transform(self, formula: str):
        tree = ast.parse(formula)
        for a in ast.walk(tree):
            # replace variables with inputs
            if isinstance(a, Name) and a.id in self.inputs.keys():
                a.id = f"self.inputs[\"{a.id}\"]"
        new_formula = ast.unparse(tree)
        try:
            result: NDArray[np.float64] = eval(new_formula)
        except Exception as e:
            print(e)
            result = np.zeros(len(list(self.inputs.values())[0]))

        return result


class MechanismContainer(html.Div):
    def __init__(self, id, node, edges):
        super().__init__(id=id)
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.children = []
        self.children.append(html.Label(f"variable: {node}"))
        self.children.append(html.Hr())
        self.children.append(html.P("affected by: "+", ".join(list(edges))))
        self.children.extend([
            html.Label(f"f({', '.join(sorted(list(edges)))}) = "),
            InputField(
                value="",
                id={"type": "formula-field", "index": node},
                type="text"
            ),
            html.Button(
                "verify",
                id={"type": "verify-formula", "index": node}
            ),
            html.P(
                "not verified",
                id={"type": "formula-validity", "index": node},
                style={
                    "border": "2px yellow solid",
                    "margin": "2px",
                }
            )
        ])


class MechanismBuilderComponent(html.Div):
    def __init__(self, id):
        super().__init__(id=id)
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.graph_builder = graph_builder_component.graph_builder
        self.update()

    def update(self):
        self.children = []


        for node, causes in self.graph_builder.graph_tracker.in_edges.items():
            self.children.append(
                MechanismContainer(
                    id={"type": "mechanism-container", "index": node},
                    node=node, edges=causes
                )
            )


mechanism_builder_component = MechanismBuilderComponent(
    id="mechanism-builder-component"
)

@callback(
    Output({"type": "formula-validity", "index": MATCH}, "style"),
    Output({"type": "formula-validity", "index": MATCH}, "children"),
    Input({"type": "verify-formula", "index": MATCH}, "n_clicks"),
    State({"type": "formula-field", "index": MATCH}, "value"),
    prevent_initial_call=True
)
def verify(_, input_formula: str):
    triggered_id = ctx.triggered_id
    if not triggered_id:
        raise PreventUpdate

    variable = triggered_id.get("index")
    assert variable, "error"


    if not input_formula:
        return(
            {
                "border": "2px yellow solid",
                "margin": "2px",
            },
            "no formula"
        )
    elif input_formula.isdigit():
        return(
            {
                "border": "2px green solid",
                "margin": "2px",
            },
            "valid formula"
        )
    else:
        return(
            {
                "border": "2px red solid",
                "margin": "2px",
            },
            "invalid formula"
        )

if __name__ == "__main__":
    x = np.random.random(size=5)
    y = np.random.random(size=5)
    z = np.random.random(size=5)
    re = RegressionMechanism({"x": x, "y": y, "z": z})
    print(re.transform("sqrt(x)+cos(y)"))
    print(re.transform("-1*(y*10 - x + x) + y ** x + exp(z)"))

    cl = ClassificationMechanism({"x": x, "y": y, "z": z})
    conditions = ["x < 0.2", "x > 0.8"]
    print(cl.transform(conditions))
    conditions = ["x < 0.2", "(0.2 <= x) & (x < 0.8)"]
    print(cl.transform(conditions))

