import dash_bootstrap_components as dbc
from dash import html, dcc

from models.graph import graph
from models.mechanism import MechanismType
from utils.latexify import py_to_latex

from utils.parser import funcs


class MechanismBuilder(html.Div):
    def __init__(self):
        super().__init__(id="mechanism-builder")
        self.style = {
            "border": "3px green solid",
            "margin": "3px",
        }
        self.children = [
            VariableSelection(),
            html.Hr(),
            MechanismConfig()
        ]


class VariableSelection(html.Div):
    variable: str | None = None
    def __init__(self):
        super().__init__(id="variable-selection-mechanism")
        nodes = graph.get_nodes()
        node_ids = graph.get_node_ids()
        assert len(node_ids) > 0
        if VariableSelection.variable is None:
            VariableSelection.variable = node_ids[0]

        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None

        if node.mechanism_metadata.mechanism_type == "regression":
            button_id = "confirm-regression"
        else:
            button_id = "confirm-classification"

        self.children = [
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        options={x.id_: x.name or x.id_ for x in nodes},
                        value=VariableSelection.variable,
                        id="mechanism-builder-target-node",
                        searchable=False,
                        clearable=False
                    )
                ),
                dbc.Col(html.Button("Confirm Mechanism", id=button_id, n_clicks=0)),
                dbc.Col(html.P("some placeholder for verification")),
            ])
        ]


class MechanismConfig(html.Div):
    mechanism_type: MechanismType | None = None
    operators_regression: str = ", ".join(["+", "-", "*", "/", "**", "//", "%"])
    operators_classfication: str = ", ".join(
        ["+", "-", "*", "/", "**", "//", "%", ">", "<", ">=", "<=", "==", "!=", "&", "|", "^"]
    )
    functions: str = ", ".join(funcs.keys())
    is_open: bool = False
    def __init__(self):
        super().__init__(id="mechanism-config")
        assert VariableSelection.variable is not None
        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None
        if MechanismConfig.mechanism_type is None:
            MechanismConfig.mechanism_type = node.mechanism_metadata.mechanism_type

        causes = [x.name or x.id_ for x in node.in_nodes]
        causes.append(f"n_{node.name or node.id_}")
        causes = ", ".join(causes)

        print(f"is_open: {MechanismConfig.is_open}")

        self.children = []
        if MechanismConfig.mechanism_type == "regression":
            self.children.extend(
                [
                    dbc.Row([
                        dbc.Col(
                            dcc.RadioItems(
                                options=["regression", "classification"],
                                value=MechanismConfig.mechanism_type,
                                id="mechanism-choice",
                            ),
                        ),
                    ]),
                    dbc.Row(html.Button("toggle help", id="toggle-help-regression")),
                    dbc.Row(dbc.Collapse(
                        [
                            dbc.Card([
                                dbc.CardHeader("Causes:"),
                                dbc.CardBody(causes)
                            ]),
                            dbc.Card([
                                dbc.CardHeader("Operators:"),
                                dbc.CardBody(MechanismConfig.operators_regression)
                            ]),
                            dbc.Card([
                                dbc.CardHeader("Functions:"),
                                dbc.CardBody(MechanismConfig.functions)
                            ]),
                        ],
                        id="collapse-regression", is_open=MechanismConfig.is_open
                    )),
                ],
            )
        else:
            self.children.extend([
                dbc.Row([
                    dbc.Col(
                        dcc.RadioItems(
                            options=["regression", "classification"],
                            value=MechanismConfig.mechanism_type,
                            id="mechanism-choice",
                        ),
                    ),
                    dbc.Col(
                        html.Button("Add Class", id="add-class", n_clicks=0)
                    ),
                ]),

                dbc.Row(html.Button("toggle help", id="toggle-help-classification")),
                dbc.Row(dbc.Collapse(
                    [
                        dbc.Card([
                            dbc.CardHeader("Causes:"),
                            dbc.CardBody(causes)
                        ]),
                        dbc.Card([
                            dbc.CardHeader("Operators:"),
                            dbc.CardBody(MechanismConfig.operators_classfication)
                        ]),
                        dbc.Card([
                            dbc.CardHeader("Functions:"),
                            dbc.CardBody(MechanismConfig.functions)
                        ]),
                        dbc.Card([
                            dbc.CardHeader("Note:"),
                            dbc.CardBody(
                                "expressions evaluated to booleans need to wrapped in parenthesis e.g.:\n"
                                "'(a > 3) & (b > 2)' works, but 'a > 3 & b > 2' does not work"
                            )
                        ]),
                    ],
                    id="collapse-classification", is_open=MechanismConfig.is_open
                )),
            ])

        self.children.extend([
            dbc.Row(html.Hr()),
            dbc.Row(MechanismInput()),
        ])


class MechanismInput(html.Div):
    def __init__(self):
        super().__init__(id="mechanism-input")
        assert VariableSelection.variable is not None
        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None

        match node.mechanism_metadata.mechanism_type:
            case "regression":
                self.children = RegressionBuilder()
            case "classification":
                self.children = ClassificationBuilder()


class RegressionBuilder(html.Div):
    def __init__(self):
        super().__init__(id="regression-builder")
        assert VariableSelection.variable is not None
        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None

        displayed_names = [x.name or x.id_ for x in node.in_nodes]
        displayed_names.append(f"n_{{ {node.name or node.id_} }}")

        formula = node.mechanism_metadata.formulas.get("0")
        assert formula is not None

        self.children = [
            dbc.Row([
                dbc.Col(
                    dcc.Markdown(f"$$f({', '.join(displayed_names)}):=$$", mathjax=True),
                    width="auto", style={"paddingTop": "10px"}
                ),
                dbc.Col(dbc.Input(id="regression-input", value=formula)),
            ])
        ]


class ClassificationBuilder(html.Div):
    def __init__(self):
        super().__init__(id="classification-builder")
        self.children = []
        assert VariableSelection.variable is not None
        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None
        displayed_names = [x.name or x.id_ for x in node.in_nodes]
        displayed_names.append(f"n_{{ {node.name or node.id_} }}")
        displayed_names = ", ".join(displayed_names)
        for c, f in node.mechanism_metadata.get_formulas().items():
            self.children.append(
                dbc.Row([
                    dbc.Col(
                        dcc.Markdown(f"$$class_{{{c}}}: f({displayed_names}):=$$", mathjax=True),
                        width="auto", style={"paddingTop": "10px"}
                    ),
                    dbc.Col(dbc.Input(
                        id={"type": "classification-input", "index": c}, value=f
                    )),
                    dbc.Col(
                        html.Button("Remove Class", id={"type": "remove-class", "index": c}, n_clicks=0),
                        width="auto")
                ], align="center", className="g-0")
            )
        self.children.append(
            dcc.Markdown("$$class_{else}: \\text{all data points not classified by the above functions}$$", mathjax=True)
        )


class MechanismViewer(html.Div):
    error: str | None = "invalid formula"
    # TODO: depending on chosen node on left -> only show
    def __init__(self):
        super().__init__(id="mechanism-viewer")
        assert VariableSelection.variable is not None
        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None

        in_nodes = [x.name or x.id_ for x in node.in_nodes]
        in_nodes.append(f"n_{node.name or node.id_}")
        causes = ", ".join(in_nodes)

        self.children = []
        if MechanismViewer.error is not None:
            self.children.append(dbc.Alert(MechanismViewer.error, color="danger"))
        else:
            self.children.append(dbc.Alert("mechanism OK", color="success"))

        formulas = node.mechanism_metadata.get_formulas()
        mechanism_type = node.mechanism_metadata.mechanism_type
        if mechanism_type == "regression":
            try:
                x = py_to_latex(f"f({causes})", in_nodes)
                y = py_to_latex(f"{list(formulas.values())[0]}", in_nodes)
                latex_formula = x + ":=" + y
            except:
                latex_formula = py_to_latex(f"f({causes})", in_nodes) + " := \\text{<invalid>}"
            self.children.append(
                dcc.Markdown(f"$${latex_formula}$$", mathjax=True)
            )
        else:
            for class_id, formula in formulas.items():
                # TODO: replace all python formulas with equivalent latex formulas
                # formula = formula.replace(f"n_{to_replace}", f"n_{{ {to_replace} }}").replace("&", "\wedge")
                try:
                    x = py_to_latex(f"f_{class_id}({causes})", in_nodes)
                    y = py_to_latex(f"{formula}", in_nodes)
                    latex_formula = x + ":=" + y
                except:
                    latex_formula = py_to_latex(f"f_{class_id}({causes})", in_nodes) + " := \\text{<invalid>}"
                self.children.append(
                    dcc.Markdown(f"$${latex_formula}$$", mathjax=True)
            )
