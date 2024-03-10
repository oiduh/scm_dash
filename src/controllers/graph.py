from dash import ALL, callback, Output, Input, State, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from views.graph import GraphBuilder
from views.mechanism import MechanismBuilder
from views.noise import NoiseBuilder


def setup_callbacks():
    @callback(
        Output("graph-builder", "children", allow_duplicate=True),
        Output("noise-builder", "children", allow_duplicate=True),
        Output("mechanism-builder", "children", allow_duplicate=True),
        Input("add-node-button", "n_clicks"),
        prevent_initial_call=True
    )
    def add_node(clicked):
        if not clicked:
            raise PreventUpdate

        graph.add_node()
        return GraphBuilder().children, NoiseBuilder().children, MechanismBuilder().children

    @callback(
        Output("graph-builder", "children", allow_duplicate=True),
        Output("noise-builder", "children", allow_duplicate=True),
        Output("mechanism-builder", "children", allow_duplicate=True),
        Input({"type": "remove-node-button", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def remove_node(clicked):
        if not any(clicked):
            raise PreventUpdate

        triggered_node: dict | None = ctx.triggered_id
        if not triggered_node or not (node_id := triggered_node.get("index")):
            raise PreventUpdate

        graph.remove_node(graph.get_node_by_id(node_id))
        return GraphBuilder().children, NoiseBuilder().children, MechanismBuilder().children

    @callback(
        Output("graph-builder", "children", allow_duplicate=True),
        Output("mechanism-builder", "children", allow_duplicate=True),
        Input({"type": "add-edge-button", "index": ALL}, "n_clicks"),
        State({"type": "add-edge-choice", "index": ALL}, "value"),
        State({"type": "add-edge-choice", "index": ALL}, "id"),
        prevent_initial_call=True
    )
    def add_edge(_, choices, ids):
        context: dict | None = ctx.triggered_id
        if not context:
            raise PreventUpdate
        triggered_node = context.get("index")
        if not triggered_node:
            raise PreventUpdate
        index = [x.get("index") for x in ids].index(triggered_node)
        target_node_id = choices[index]
        if not target_node_id:
            raise PreventUpdate
        source = graph.get_node_by_id(triggered_node)
        target = graph.get_node_by_id(target_node_id)
        if not graph.can_add_edge(source, target):
            raise PreventUpdate
        graph.add_edge(source, target)
        return GraphBuilder().children, MechanismBuilder().children

    @callback(
        Output("graph-builder", "children", allow_duplicate=True),
        Output("mechanism-builder", "children", allow_duplicate=True),
        Input({"type": "remove-edge-button", "index": ALL}, "n_clicks"),
        State({"type": "remove-edge-choice", "index": ALL}, "value"),
        State({"type": "remove-edge-choice", "index": ALL}, "id"),
        prevent_initial_call=True
    )
    def remove_edge(_, choices, ids):
        context: dict | None = ctx.triggered_id
        if not context:
            raise PreventUpdate
        triggered_node = context.get("index")
        if not triggered_node:
            raise PreventUpdate
        index = [x.get("index") for x in ids].index(triggered_node)
        target_node_id = choices[index]
        if not target_node_id:
            raise PreventUpdate
        source = graph.get_node_by_id(triggered_node)
        target = graph.get_node_by_id(target_node_id)
        if target.id not in source.get_out_node_ids():
            raise PreventUpdate
        graph.remove_edge(source, target)
        return GraphBuilder().children, MechanismBuilder().children

    @callback(
        Output("network-graph", "elements"),
        Input("graph-builder", 'children')
    )
    def update_graph(*_):
        nodes = [{"data": {"id": cause, "label": cause}} for cause in graph.get_node_ids()]
        edges = []
        for cause in graph.get_nodes():
            for effect in cause.out_nodes:
                edges.append({"data": {"source": cause.id, "target": effect.id}})
        return nodes + edges
    
