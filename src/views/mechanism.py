import dash_bootstrap_components as dbc
from dash import html, dcc

from models.graph import graph
from models.mechanism import MechanismType


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
    def __init__(self):
        super().__init__(id="mechanism-config")
        assert VariableSelection.variable is not None
        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None
        if MechanismConfig.mechanism_type is None:
            MechanismConfig.mechanism_type = node.mechanism_metadata.mechanism_type

        self.children = []
        if MechanismConfig.mechanism_type == "regression":
            self.children.append(
                dbc.Row([
                    dbc.Col(
                        dcc.RadioItems(
                            options=["regression", "classification"],
                            value=MechanismConfig.mechanism_type,
                            id="mechanism-choice",
                        ),
                    ),
                ])
            )
        else:
            self.children.append(
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
                ])
            )

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
            dcc.Markdown(f"$$f({', '.join(displayed_names)})=$$", mathjax=True),
            dbc.Col([
                dbc.Row(
                    dbc.Col(
                        dbc.Textarea(
                            id="regression-input",
                            value=formula,
                            debounce=False,
                            required=True,
                        )
                    )
                ),
            ]),
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
                        dcc.Markdown(f"$$class_{{{c}}}: f({displayed_names})=$$", mathjax=True),
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
            # TODO: fix this shit
            html.P("else: 'TODO -> rest that dont fit in other classes'")
        )


class MechanismViewer(html.Div):
    # TODO: depending on chosen node on left -> only show
    def __init__(self):
        super().__init__(id="mechanism-viewer")
        assert VariableSelection.variable is not None
        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None

        in_nodes = [x.name or x.id_ for x in node.in_nodes]
        in_nodes.append(f"n_{{ {node.name or node.id_} }}")
        causes = ", ".join(in_nodes)

        self.children = []
        self.children.append(
            dbc.Alert(
                "this is warning",
                color="warning"
            )
        )
        self.children.append(
            dbc.Alert(
                "this is danger",
                color="danger"
            )
        )
        formulas = node.mechanism_metadata.get_formulas()
        mechanism_type = node.mechanism_metadata.mechanism_type
        if mechanism_type == "regression":
            self.children.append(
                dcc.Markdown(f"$$f({causes}) = {list(formulas.values())[0]}$$", mathjax=True)
            )
        else:
            to_replace = node.name or node.id_
            for class_id, formula in formulas.items():
                # TODO: replace all python formulas with equivalent latex formulas
                formula = formula.replace(f"n_{to_replace}", f"n_{{ {to_replace} }}").replace("&", "\wedge")
                self.children.append(
                    dcc.Markdown(f"$$f_{{ {class_id} }}({causes}) = {formula}$$", mathjax=True)
            )
