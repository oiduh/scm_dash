from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash_cytoscape import Cytoscape


from models.graph import graph



# A) graph builder -> dropdowns etc.

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
        for name in graph.get_node_names():
            accordion.children.append(dbc.AccordionItem(NodeBuilder(name), title=name))
        self.children.append(accordion)
        self.children.append(html.Div(html.Button("Add Node", id="add-node-button")))


class NodeBuilder(html.Div):
    def __init__(self, id: str):
        super().__init__(id={"type": "node-builder", "index": id})
        self.style = {
            "border": "3px green solid",
            "margin": "3px",
        }
        in_nodes = graph.get_node_by_id(id).get_in_node_ids()
        out_nodes = graph.get_node_by_id(id).get_out_node_ids()
        can_add = []
        for node in graph.get_node_ids():
            if graph.can_add_edge(graph.get_node_by_id(id), graph.get_node_by_id(node)):
                can_add.append({"label": node, "value": node, "disabled": False})
            else:
                can_add.append({"label": f"{node} (cycle)", "value": node, "disabled": True})
        can_remove = out_nodes
        self.children = [
            dbc.Row([
                dbc.Col([
                    dbc.Row(html.Div(f"node id: {id}")),
                    dbc.Row(html.Div("in nodes: " + ', '.join(in_nodes))),
                    dbc.Row(html.Div("out nodes: " + ', '.join(out_nodes))),
                ]),
                dbc.Col([
                    dbc.Row(html.Div("Add Edge")),
                    dbc.Row([
                        dbc.Col(dcc.Dropdown(
                            options=can_add, searchable=False,
                            id={"type": "add-edge-choice", "index": id}
                        )),
                        dbc.Col(html.Button("Confirm", id={"type": "add-edge-button","index": id}))
                    ], className="g-0")
                ]),
                dbc.Col([
                    dbc.Row(html.Div("Remove Edge")),
                    dbc.Row([
                        dbc.Col(dcc.Dropdown(
                            options=can_remove, searchable=False,
                            id={"type": "remove-edge-choice", "index": id}
                        )),
                        dbc.Col(html.Button("Confirm", id={"type": "remove-edge-button","index": id}))
                    ], className="g-0")
                ]),
            ]),
            html.Div(html.Button("Remove Node", id={"type": "remove-node-button", "index": id}))
        ]


# B) graph view -> show nodes + directed edges
class GraphViewer(html.Div):
    """singleton graph viewer class"""
    def __init__(self):
        super().__init__(id= "graph-viewer")
        self.style = {}  # TODO: at last
        self.children = [Cytoscape(
            id="network-graph", layout={"name": "circle"},
            userPanningEnabled=False,
            zoomingEnabled=False,
            # TODO: use stylesheets for arrows and style
            # give attributes to nodes (cause/effect)
            # assign actual mechanism to edges
            # different colors for special nodes/edges
            style={"width": "100%", "height": "700px"},
            elements=[],
            stylesheet=[
                {
                    "selector": "node",
                    "style": {
                        "label": "data(label)"
                    }
                },
                {
                    "selector": "edge",
                    "style": {
                        "curve-style": "bezier",
                        "target-arrow-shape": "triangle",
                        "arrow-scale": 2
                    }
                }
            ]
        )]


if __name__ == "__main__":
    app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
    app.layout = html.Div([
        html.Div("causality app"),
        html.Hr(),
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div("PLACEHOLDER", id="first-component")
                ]),
                dbc.Col([
                    html.Div("PLACEHOLDER", id="second-component")
                ])
            ])
        ])
    ])
    app.run(debug=True,)

