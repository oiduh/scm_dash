import dash_bootstrap_components as dbc
from dash import Dash, dcc, html
from dash_cytoscape import Cytoscape

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
        accordion = dbc.Accordion(always_open=True)
        accordion.children = []
        for id_ in graph.get_node_ids():  # TODO: get node names when available
            accordion.children.append(dbc.AccordionItem(NodeBuilder(id_), title=id_))
        self.children.append(accordion)
        self.children.append(html.Div(html.Button("Add Node", id="add-node-button")))


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

    def __init__(self) -> None:
        super().__init__(id="graph-viewer")
        self.style = {}
        self.children = [
            Cytoscape(
                id="network-graph",
                layout={"name": "circle"},
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
