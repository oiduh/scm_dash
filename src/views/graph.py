import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash_cytoscape import Cytoscape
from enum import Enum
from dash import dcc

from models.graph import graph


class GraphBuilder(html.Div):
    def __init__(self):
        super().__init__(id="graph-builder-new")
        self.style = {
            "border": "3px green solid",
            "margin": "3px",
        }
        self.children = []
        variable_selection = VariableSelection()
        first_node = graph.get_nodes()[0]
        VariableSelection.selected_node_id = first_node.id_
        self.children.append(variable_selection)
        self.children.append(html.Hr()) # TODO: better distinction from rest
        self.children.append(VariableConfig())

    @staticmethod
    def get_graph_data():
        nodes = [
            {"data": {"id": cause, "label": cause}} for cause in graph.get_node_ids()
        ]
        edges = []
        for cause in graph.get_nodes():
            for effect in cause.out_nodes:
                edges.append({"data": {"source": cause.id_, "target": effect.id_}})
        return nodes + edges


class VariableSelection(html.Div):
    selected_node: str
    def __init__(self):
        super().__init__(id="variable-selection")
        nodes = graph.get_nodes()
        node_ids = [node.id_ for node in nodes]
        assert len(node_ids) > 0
        VariableSelection.selected_node_id = node_ids[0]

        self.children = []
        self.children.append(
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        options=node_ids,
                        value=VariableSelection.selected_node_id,
                        id="graph-builder-target-node",
                        searchable=False,
                        clearable=False
                    )
                ),
                dbc.Col(html.Button("Remove Selected Node", id="remove-selected-node", n_clicks=0)),
                dbc.Col(html.Button("Add New Node", id="add-new-node", n_clicks=0)),
            ])
        )


class VariableConfig(html.Div):
    def __init__(self):
        super().__init__(id="variable-config")
        selected_node = graph.get_node_by_id(VariableSelection.selected_node_id)
        assert selected_node is not None
        in_node_ids = selected_node.get_in_node_ids()

        can_add: list[str] = []
        for other_node_id in graph.get_node_ids():
            target_node = graph.get_node_by_id(other_node_id)
            assert target_node is not None
            if graph.can_add_edge(selected_node, target_node):
                can_add.append(target_node.id_)

        can_remove = selected_node.get_out_node_ids()

        self.children = []
        self.children.extend([
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col(html.P(f"Rename Variable:")),
                        dbc.Col(dcc.Input(
                            type="text",
                            minLength=1,
                            maxLength=16,
                        )),
                        dbc.Col(html.Button("Confirm New Name", id="confirm-new-name", n_clicks=0)),
                    ]),
                ]),
                html.Hr()
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col(html.P(f"In-Nodes:")),
                        dbc.Col(html.P(','.join(in_node_ids) or '<None>')),
                    ]),
                    dbc.Row([
                        dbc.Col(html.P(f"Out-Nodes:")),
                        dbc.Col(html.P(','.join(can_remove) or '<None>')),
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
                            clearable=False
                        )),
                        dbc.Col(html.Button("Add Edge", id="add-new-edge", n_clicks=0)),
                    ]),
                    dbc.Row([
                        dbc.Col(html.P(f"Select Out-Node to Remove")),
                        dbc.Col(dcc.Dropdown(
                            options=can_remove,
                            value=None,
                            id="remove-out-node",
                            searchable=False,
                            clearable=False
                        )),
                        dbc.Col(html.Button("Remove Edge", id="remove-edge", n_clicks=0))
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
        self.style = {}
        self.children = [
            dcc.Dropdown(
                options=self.Layouts.get_all(),
                value=self.LAYOUT,
                id="layout-choices",
                searchable=False,
                multi=False,
                clearable=False
            ),
            html.H3(f"Layout: {GraphViewer.LAYOUT}"),
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

