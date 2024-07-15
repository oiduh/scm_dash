import ast
from ast import Name
from typing import Any, Dict

import numpy as np
from dash import MATCH, Input, Output, State, callback, html
from dash.dcc import Input as InputField
from dash.dcc import RadioItems
from dash.exceptions import PreventUpdate
from numpy.typing import NDArray

from graph_builder import graph_builder_component

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
        raise NotImplemented()


class ClassificationMechanism(BaseMechanism):
    def __init__(self, inputs: Dict[str, np.ndarray]):
        super().__init__(inputs)

    def transform(self, formulas: list[str]):
        print(formulas)
        results = np.full((len(formulas), len(list(self.inputs.values())[0])), False)

        failed = False
        for idx, formula in enumerate(formulas):
            print(idx, formula)
            tree = ast.parse(formula)
            for a in ast.walk(tree):
                if isinstance(a, Name) and a.id in self.inputs.keys():
                    a.id = f'self.inputs["{a.id}"]'
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

        results = np.vstack(
            [results, np.full(len(list(self.inputs.values())[0]), False)]
        )
        for idx, col in enumerate(np.sum(results, axis=0)):
            if col == 0:
                results[-1][idx] = True

        if not np.any(results[-1]):
            results = results[:-1]

        if np.prod(np.sum(results, axis=0)) != 1.0:
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
                a.id = f'self.inputs["{a.id}"]'
        new_formula = ast.unparse(tree)
        try:
            result: NDArray[np.float64] = eval(new_formula)
        except Exception as e:
            print(e)
            result = np.zeros(len(list(self.inputs.values())[0]))

        return result


class RegressionInputComponent(html.Div):
    def __init__(self, id: dict[str, str]):
        super().__init__(id=id)
        node = id["index"]
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.children = [
            InputField(
                value="", id={"type": "formula-field", "index": node}, type="text"
            ),
        ]


class ClassificationInputComponent(html.Div):
    def __init__(self, id: dict[str, str]):
        super().__init__(id=id)
        node = id["index"]
        self.id = id
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        # initial class structure -> 2 classes: consequence and alternative
        self.classes = 2
        self.children = []
        self.children.append(
            html.Div(
                id={"type": "class-container", "index": node},
                children=[
                    html.Div(
                        children=[
                            html.Label(f"class 1:  if "),
                            InputField(
                                value="",
                                id={
                                    "type": "class-formula-field",
                                    "index": f"{node}-1",
                                },
                                type="text",
                            ),
                            html.Button(
                                "remove class",
                                id={"type": "remove-class", "index": f"{node}-1"},
                            ),
                        ]
                    )
                ],
            )
        )
        self.children.append(
            html.Div(
                children=[
                    html.Label("class 2: else"),
                ]
            )
        )
        self.children.append(
            html.Button("add class", id={"type": "add-class", "index": node}),
        )

    def add_class(self):
        button = self.children[-1]
        self.children = self.children[:-2]
        self.children.append(
            html.Div(
                id={"type": "class-container", "index": id},
                children=[
                    html.Div(
                        children=[
                            html.Label(f"class {self.classes}:  if "),
                            InputField(
                                value="",
                                id={
                                    "type": "class-formula-field",
                                    "index": f"{self.id}-{self.classes}",
                                },
                                type="text",
                            ),
                            html.Button(
                                "remove class",
                                id={
                                    "type": "remove-class",
                                    "index": f"{self.id}-{self.classes}",
                                },
                            ),
                        ]
                    )
                ],
            )
        )
        self.classes += 1
        self.children.append(
            html.Div(
                children=[
                    html.Label(f"class {self.classes}: else"),
                ]
            )
        )
        self.children.append(button)

    def remove_class(self):
        pass


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
        self.children.append(html.P("affected by: " + ", ".join(list(edges))))
        self.children.extend(
            [
                RadioItems(
                    id={"type": "mechanism-option", "index": node},
                    options=["regression", "classification"],
                    value="regression",
                    inline=True,
                ),
                html.Div(
                    id={"type": "mechanism-choice", "index": node},
                    children=[
                        RegressionInputComponent(
                            id={"type": "regression-component", "index": node}
                        ),
                        # ClassificationInputComponent(id={"type": "classification-component", "index": node})
                    ],
                ),
            ]
        )


class MechanismBuilderComponent(html.Div):
    def __init__(self, id):
        super().__init__(id=id)
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.graph_tracker = graph_builder_component.graph_builder.graph_tracker
        self.update()

    def update(self):
        self.children = []

        for node, causes in self.graph_tracker.in_edges.items():
            self.children.append(
                MechanismContainer(
                    id={"type": "mechanism-container", "index": node},
                    node=node,
                    edges=causes,
                )
            )


mechanism_builder_component = MechanismBuilderComponent(
    id="mechanism-builder-component"
)


@callback(
    Output(
        {"type": "mechanism-choice", "index": MATCH}, "children", allow_duplicate=True
    ),
    Input({"type": "mechanism-option", "index": MATCH}, "value"),
    State({"type": "mechanism-option", "index": MATCH}, "id"),
    prevent_initial_call=True,
)
def mechanism_type(choice: str, id_dict: dict[str, str]):
    node_id = id_dict["index"]
    causes = mechanism_builder_component.graph_tracker.in_edges[node_id]
    match choice:
        case "regression":
            print("regression")
            return RegressionInputComponent(
                id={"type": "regression-component", "index": node_id}
            )
        case "classification":
            print("classification")
            return ClassificationInputComponent(
                id={"type": "classification-component", "index": node_id}
            )
        case _:
            raise PreventUpdate


@callback(
    Output({"type": "mechanism-choice", "index": MATCH}, "children"),
    Input({"type": "add-class", "index": MATCH}, "n_clicks"),
    State({"type": "mechanism-choice", "index": MATCH}, "children"),
    State({"type": "classification-component", "index": MATCH}, "id"),
    prevent_initial_call=True,
)
def add_class(button, current, id_):
    # must be classification component
    comp = id_["type"]
    id_ = id_["index"]
    print(f"add new class to '{comp}'-'{id_}'")
    print(f"clicked: {button}")
    print(current)
    return current


@callback(
    Output({"type": "classification-component", "index": MATCH}, "children"),
    Input({"type": "remove-class", "index": MATCH}, "n_clicks"),
    # State({"type": "classification-component", "index": MATCH}, "children"),
    # State({"type": "classification-component", "index": MATCH}, "id"),
    prevent_initial_call=True,
)
def remove(button):
    pass


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
