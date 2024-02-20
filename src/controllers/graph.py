from dash import ALL, callback, Output, Input, State, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from views.graph import GraphBuilder


def setup_callbacks():
    @callback(
        Output("graph-builder", "children", allow_duplicate=True),
        Input("add-node-button", "n_clicks"),
        prevent_initial_call=True
    )
    def add_node(clicked):
        if not clicked:
            raise PreventUpdate

        print("adding")

        graph.add_node()
        return GraphBuilder().children

    @callback(
        Output("graph-builder", "children", allow_duplicate=True),
        Input({"type": "remove-node-button", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def remove_node(clicked):
        if not any(clicked):
            raise PreventUpdate

        triggered_node: dict | None = ctx.triggered_id
        if not triggered_node or not (node_id := triggered_node.get("index")):
            raise PreventUpdate

        print(f"removing: {node_id}")
        graph.remove_node(graph.get_node_by_id(node_id))
        return GraphBuilder().children

