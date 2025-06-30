import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash_cytoscape import Cytoscape
from enum import Enum
from dash import dcc
from typing import Any

from models.graph import graph
from models.noise import CONSTANTS


class GraphUploader(html.Div):
    last_uploaded_graph: bool | None = None
    def __init__(self):
        super().__init__(id="graph-uploader")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
        self.children = []
        self.children.extend([
            html.H5("Import Graph:"),
            dcc.Upload(
                id="graph-upload-field",
                children=html.Div([
                    "Drag and drop or select file",
                ]),
                style={
                    'width': 'auto',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '8px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=False
            )
        ])
        msg_args = dict[str, Any]()
        button_args: dict[str, Any] = {
            "id": "use-graph-button",
        }
        match GraphUploader.last_uploaded_graph:
            case True:
                msg_args["children"] = "> Graph is valid"
                msg_args["style"] = {"color": "green"}
                button_args["disabled"] = False
            case False:
                msg_args["children"] = "> Graph is invalid"
                msg_args["style"] = {"color": "red"}
                button_args["disabled"] = True
            case _:
                msg_args["children"] = ""
                button_args["disabled"] = True
        button = html.Button(
            "Use Graph",
            **button_args,
            className="one-button"
        )
        message = html.P(**msg_args)
        self.children.append(html.Div(id="uploaded-graph-test", children=[
            message, button
        ]))


class GeneralGraphConfig(html.Div):
    def __init__(self):
        super().__init__(id="general-graph-config")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
        self.children = []
        self.children.append(dbc.Row([
            dbc.Col(html.H5(
                f"Current data points = {CONSTANTS.NR_DATA_POINTS}",
                id="current-data-points"
            ), width="auto"),
        ]))
        self.children.append(dbc.Row([
            dbc.Col(html.H5(f"New data points = "), width="auto"),
            dbc.Col(dcc.Input(
                id="new-data-points",
                value=CONSTANTS.NR_DATA_POINTS,
                type="number",
                size="7",
                min=CONSTANTS.MIN_DATA_POINTS,
                max=CONSTANTS.MAX_DATA_POINTS,
                step=1,
                style={"border-radius": "8px"},
            ), width="auto"),
            dbc.Col(html.Button(
                "confirm",
                id="confirm-new-data-points",
                n_clicks=0,
                className="one-button",
            ), width="auto")
        ]))


class GraphBuilder(html.Div):
    def __init__(self):
        global graph
        super().__init__(id="graph-builder-new")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
        self.children = []
        variable_selection = VariableSelection()
        first_node = graph.get_nodes()[0]
        VariableSelection.selected_node_id = first_node.id_

        self.children.append(GeneralGraphConfig())
        self.children.append(GraphUploader())
        self.children.append(variable_selection)
        self.children.append(VariableConfig())

    @staticmethod
    def get_graph_data():
        nodes = [
            {
                "data": {"id": cause.id_, "label": cause.name or cause.id_}
            } for cause in graph.get_nodes()
        ]
        edges = []
        for cause in graph.get_nodes():
            for effect in cause.out_nodes:
                edges.append({"data": {"source": cause.id_, "target": effect}})
        return nodes + edges


class VariableSelection(html.Div):
    selected_node_id: str | None = None
    def __init__(self):
        super().__init__(id="variable-selection-graph")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
        nodes = graph.get_nodes()
        assert len(nodes) > 0
        if VariableSelection.selected_node_id is None:
            VariableSelection.selected_node_id = nodes[0].id_

        self.children = []
        self.children.extend([
            dbc.Row(html.H5("Select Variable:")),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        options={x.id_: x.name or x.id_ for x in nodes},
                        value=VariableSelection.selected_node_id,
                        id="graph-builder-target-node",
                        searchable=False,
                        clearable=False,
                        style={"border-radius": "8px"},
                    )
                ),
                dbc.Col(html.Button(
                    "Remove Selected Node",
                    id="remove-selected-node",
                    n_clicks=0,
                    className="one-button"
                )),
                dbc.Col(html.Button(
                    "Add New Node",
                    id="add-new-node",
                    n_clicks=0,
                    className="one-button"
                )),
            ])
        ])


class VariableConfig(html.Div):
    def __init__(self):
        super().__init__(id="variable-config-graph")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
        assert VariableSelection.selected_node_id is not None
        selected_node = graph.get_node_by_id(VariableSelection.selected_node_id)
        assert selected_node is not None

        can_add: dict[str, str] = {}
        for other_node_id in graph.get_node_ids():
            target_node = graph.get_node_by_id(other_node_id)
            assert target_node is not None
            if graph.can_add_edge(selected_node, target_node):
                can_add[target_node.id_] = target_node.name or target_node.id_

        in_nodes = [y for y in [graph.get_node_by_id(x) for x in selected_node.in_nodes] if y is not None]
        out_nodes = [y for y in [graph.get_node_by_id(x) for x in selected_node.out_nodes] if y is not None]
        displayed_in_nodes = [x.name or x.id_ for x in in_nodes]
        displayed_out_nodes = [x.name or x.id_ for x in out_nodes]

        self.children = []
        self.children.extend([
            dbc.Row(html.H5("Change Variable Properties:")),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col(html.P(f"In-Nodes:")),
                        dbc.Col(html.P(','.join(displayed_in_nodes) or '<empty>')),
                    ]),
                    dbc.Row([
                        dbc.Col(html.P(f"Out-Nodes:")),
                        dbc.Col(html.P(','.join(displayed_out_nodes) or '<empty>')),
                    ]),
                ]),
                html.Hr(),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col(html.P(f"Select Out-Node to Add")),
                        dbc.Col(dcc.Dropdown(
                            options=can_add,
                            value=None,
                            id="add-out-node",
                            searchable=False,
                            clearable=False,
                            style={"border-radius": "8px"}
                        )),
                        dbc.Col(html.Button(
                            "Add Edge",
                            id="add-new-edge",
                            n_clicks=0,
                            className="one-button"
                        )),
                    ]),
                    dbc.Row([
                        dbc.Col(html.P(f"Select Out-Node to Remove")),
                        dbc.Col(dcc.Dropdown(
                            options=displayed_out_nodes,
                            value=None,
                            id="remove-out-node",
                            searchable=False,
                            clearable=False,
                            style={"border-radius": "8px"}
                        )),
                        dbc.Col(html.Button(
                            "Remove Edge",
                            id="remove-edge",
                            n_clicks=0,
                            className="one-button"
                        ))
                    ]),
                ]),
            ]),
        ])


class GraphViewer(html.Div):
    """singleton graph viewer class"""
    class Layouts(str, Enum):
        circle = "circle"
        random = "random"
        grid = "grid"
        concentric = "concentric"
        breadthfirst = "breadthfirst"
        # cose = "cose"
        # cose_bilkent = "cose-bilkent"
        cola = "cola"
        # euler = "euler"
        spread = "spread"
        # dagre = "dagre"
        # klay = "klay"

        @classmethod
        def get_all(cls):
            return [e.value for e in cls]

    LAYOUT: str = Layouts.circle.value

    def __init__(self) -> None:
        super().__init__(id="graph-viewer")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
        self.children = [
            html.H5("Select Layout:"),
            dcc.Dropdown(
                options=self.Layouts.get_all(),
                value=self.LAYOUT,
                id="layout-choices",
                searchable=False,
                multi=False,
                clearable=False,
                style={"border-radius": "8px"}
            ),
            Cytoscape(
                id="network-graph",
                layout={"name": self.LAYOUT},
                userPanningEnabled=False,
                zoomingEnabled=False,
                style={"width": "100%", "height": "700px"},
                elements=GraphBuilder.get_graph_data(),
                stylesheet=[
                    {"selector": "node", "style": {"label": "data(label)"}},
                    {
                        "selector": "edge",
                        "style": {
                            "curve-style": "bezier",
                            "target-arrow-shape": "triangle",
                            "arrow-scale": 2,
                        },
                    },
                ],
            )
        ]

