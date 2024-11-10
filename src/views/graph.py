import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash_cytoscape import Cytoscape
from enum import Enum
from dash import dcc

from models.graph import graph


class GraphBuilder(html.Div):
    """singleton graph builder class"""

    def __init__(self):
        super().__init__(id="graph-builder")
        self.style = {
            "border": "3px green solid",
            "margin": "3px",
        }
        self.children = []
        accordion = dbc.Accordion(start_collapsed=True)
        accordion.children = []
        for id_ in graph.get_node_ids():  # TODO: get node names when available
            accordion.children.append(dbc.AccordionItem(NodeBuilder(id_), title=id_))
        self.children.append(accordion)
        self.children.append(html.Div(html.Button("Add Node", id="add-node-button")))


class GraphBuilderNew(html.Div):
    def __init__(self):
        super().__init__(id="graph-builder-new")
        self.style = {
            "border": "3px green solid",
            "margin": "3px",
        }
        self.children = []
        variable_selection = VariableSelection()
        self.children.append(variable_selection)
        self.children.append(html.Hr()) # TODO: better distinction from rest
        self.children.append(VariableConfig(variable_selection.selected_node))


class VariableSelection(html.Div):
    def __init__(self):
        super().__init__(id="variable-selection")
        nodes = graph.get_nodes()
        node_ids = [node.id_ for node in nodes]
        assert len(node_ids) > 0
        selected_node_id = node_ids[0]

        self.selected_node = selected_node_id
        self.children = []
        self.children.append(
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        options=node_ids,
                        value=selected_node_id,
                        id="graph-builder-target-node",
                        searchable=False,
                        clearable=False
                    )
                ),
                dbc.Col(html.Button("Remove Selected Node")),
                dbc.Col(html.Button("Add New Node",id="confirm-selection")),
            ])
        )



from dash import callback, Output, Input
from dash.exceptions import PreventUpdate
@callback(
    Output("variable-config", "children", allow_duplicate=True),
    Input("graph-builder-target-node", "value"),
    Input("confirm-selection", "n_clicks"),
    # prevent_initial_call=True
    prevent_initial_call="initial_duplicate"
)
def select_node(selected_node_id: str, clicked):
    print(1)
    if not clicked:
        raise PreventUpdate
    print(2)
    return VariableConfig(selected_node_id).children


class VariableConfig(html.Div):
    def __init__(self, selected_node_id: str):
        super().__init__(id="variable-config")
        selected_node = graph.get_node_by_id(selected_node_id)
        assert selected_node is not None
        in_node_ids = selected_node.get_in_node_ids()

        can_add: list[str] = []
        for other_node_id in in_node_ids:
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
                        dbc.Col(dcc.Input()), # TODO: restrictions e.g. length, first char
                        dbc.Col(html.Button("Confirm New Name")),
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
                        dbc.Col(html.P(f"Select In-Node to Add")),
                        dbc.Col(dcc.Dropdown(
                            options=can_add,
                            value=can_add[0] if len(can_add) > 0 else None,
                            id="remove-out-node",
                            searchable=False,
                            clearable=False
                        )),
                        dbc.Col(html.Button("Add Edge"))
                    ]),
                ]),
                html.Hr()
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col(html.P(f"Out-Nodes:")),
                        dbc.Col(html.P(','.join(can_remove) or '<None>')),
                    ]),
                    dbc.Row([
                        dbc.Col(html.P(f"Select Out-Node to Remove")),
                        dbc.Col(dcc.Dropdown(
                            options=can_remove,
                            value=can_remove[0] if len(can_remove) > 0 else None,
                            id="remove-out-node",
                            searchable=False,
                            clearable=False
                        )),
                        dbc.Col(html.Button("Remove Edge"))
                    ]),
                ]),
            ]),
        ])


class NodeBuilder(html.Div):
    def __init__(self, id_: str) -> None:
        super().__init__(id={"type": "node-builder", "index": id_})
        self.style = {
            "border": "3px green solid",
            "margin": "3px",
        }
        source_node = graph.get_node_by_id(id_)
        if source_node is None:
            raise Exception("Node not found")

        in_nodes = source_node.get_in_node_ids()
        out_nodes = source_node.get_out_node_ids()

        can_add = []
        for other_node_id in graph.get_node_ids():
            target_node = graph.get_node_by_id(other_node_id)
            if target_node is None:
                continue
            if graph.can_add_edge(source_node, target_node):
                can_add.append(
                    {
                        "label": target_node.id_,
                        "value": target_node.id_,
                        "disabled": False,
                    }
                )
            else:
                can_add.append(
                    {
                        "label": f"{target_node.id_} (cycle)",
                        "value": target_node.id_,
                        "disabled": True,
                    }
                )
        can_remove = out_nodes
        self.children = [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Row(html.Div(f"node id: {id_}")),
                            dbc.Row(html.Div("in nodes: " + ", ".join(in_nodes))),
                            dbc.Row(html.Div("out nodes: " + ", ".join(out_nodes))),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Row(html.Div("Add Edge")),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Dropdown(
                                            options=can_add,
                                            searchable=False,
                                            id={
                                                "type": "add-edge-choice",
                                                "index": id_,
                                            },
                                        )
                                    ),
                                    dbc.Col(
                                        html.Button(
                                            "Confirm",
                                            id={
                                                "type": "add-edge-button",
                                                "index": id_,
                                            },
                                        )
                                    ),
                                ],
                                className="g-0",  # TODO: something to do with spacing?
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Row(html.Div("Remove Edge")),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Dropdown(
                                            options=can_remove,
                                            searchable=False,
                                            id={
                                                "type": "remove-edge-choice",
                                                "index": id_,
                                            },
                                        )
                                    ),
                                    dbc.Col(
                                        html.Button(
                                            "Confirm",
                                            id={
                                                "type": "remove-edge-button",
                                                "index": id_,
                                            },
                                        )
                                    ),
                                ],
                                className="g-0",
                            ),
                        ]
                    ),
                ]
            ),
            html.Div(
                html.Button(
                    "Remove Node", id={"type": "remove-node-button", "index": id_}
                )
            ),
        ]


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

    LAYOUT = Layouts.circle.value

    def __init__(self) -> None:
        super().__init__(id="graph-viewer")
        self.style = {}
        self.children = [
            dcc.Dropdown(
                options=self.Layouts.get_all(),
                searchable=False,
                id="layout-choices",
                multi=False,
            ),
            html.H3(f"Layout: {GraphViewer.LAYOUT}"),
            Cytoscape(
                id="network-graph",
                layout={"name": self.LAYOUT},
                userPanningEnabled=False,
                zoomingEnabled=False,
                style={"width": "100%", "height": "700px"},
                elements=[],
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


if __name__ == "__main__":
    app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
    app.layout = html.Div(
        [
            html.Div("causality app"),
            html.Hr(),
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col([html.Div("PLACEHOLDER", id="first-component")]),
                            dbc.Col([html.Div("PLACEHOLDER", id="second-component")]),
                        ]
                    )
                ]
            ),
        ]
    )
    app.run(
        debug=True,
    )
