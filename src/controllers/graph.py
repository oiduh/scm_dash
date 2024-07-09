from dash import ALL, Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from views.graph import GraphBuilder
from views.mechanism import MechanismBuilder
from views.noise import NoiseBuilder


def setup_callbacks() -> None:
    @callback(
        Output("graph-builder", "children", allow_duplicate=True),
        Output("noise-builder", "children", allow_duplicate=True),
        Output("mechanism-builder", "children", allow_duplicate=True),
        Input("add-node-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def add_node(clicked):
        if not clicked:
            raise PreventUpdate

        try:
            graph.add_node()
        except Exception as e:
            raise PreventUpdate from e

        return (
            GraphBuilder().children,
            NoiseBuilder().children,
            MechanismBuilder().children,
        )

    @callback(
        Output("graph-builder", "children", allow_duplicate=True),
        Output("noise-builder", "children", allow_duplicate=True),
        Output("mechanism-builder", "children", allow_duplicate=True),
        Input({"type": "remove-node-button", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def remove_node(clicked):
        if not any(clicked):
            raise PreventUpdate

        triggered_node: dict | None = ctx.triggered_id
        if not triggered_node or (node_id := triggered_node.get("index")) is None:
            raise PreventUpdate

        node = graph.get_node_by_id(node_id)
        if node is None:
            raise PreventUpdate

        try:
            graph.remove_node(node)
        except Exception as e:
            raise PreventUpdate from e

        return (
            GraphBuilder().children,
            NoiseBuilder().children,
            MechanismBuilder().children,
        )

    @callback(
        Output("graph-builder", "children", allow_duplicate=True),
        Output("mechanism-builder", "children", allow_duplicate=True),
        Input({"type": "add-edge-button", "index": ALL}, "n_clicks"),
        State({"type": "add-edge-choice", "index": ALL}, "value"),
        State({"type": "add-edge-choice", "index": ALL}, "id"),
        prevent_initial_call=True,
    )
    def add_edge(_, choices, ids):
        context: dict | None = ctx.triggered_id
        if context is None:
            raise PreventUpdate

        triggered_node: str | None = context.get("index")
        if triggered_node is None:
            raise PreventUpdate

        index = [x.get("index") for x in ids].index(triggered_node)
        target_node_id = choices.get(index, None)
        if target_node_id is None:
            raise PreventUpdate

        source = graph.get_node_by_id(triggered_node)
        target = graph.get_node_by_id(target_node_id)

        if source is None or target is None:
            raise PreventUpdate

        try:
            graph.add_edge(source, target)
        except Exception as e:
            raise PreventUpdate from e

        return GraphBuilder().children, MechanismBuilder().children

    @callback(
        Output("graph-builder", "children", allow_duplicate=True),
        Output("mechanism-builder", "children", allow_duplicate=True),
        Input({"type": "remove-edge-button", "index": ALL}, "n_clicks"),
        State({"type": "remove-edge-choice", "index": ALL}, "value"),
        State({"type": "remove-edge-choice", "index": ALL}, "id"),
        prevent_initial_call=True,
    )
    def remove_edge(_, choices, ids):
        context: dict | None = ctx.triggered_id
        if context is None:
            raise PreventUpdate

        triggered_node: str | None = context.get("index", None)
        if triggered_node is None:
            raise PreventUpdate

        index = [x.get("index") for x in ids].index(triggered_node)
        target_node_id = choices.get(index, None)
        if target_node_id is None:
            raise PreventUpdate

        source = graph.get_node_by_id(triggered_node)
        target = graph.get_node_by_id(target_node_id)

        if source is None or target is None:
            raise PreventUpdate

        # TODO: is this code necessary
        # if target.id_ not in source.get_out_node_ids():
        #     raise PreventUpdate

        try:
            graph.remove_edge(source, target)
        except Exception as e:
            raise PreventUpdate from e

        return GraphBuilder().children, MechanismBuilder().children

    @callback(Output("network-graph", "elements"), Input("graph-builder", "children"))
    def update_graph(*_):
        nodes = [
            {"data": {"id": cause, "label": cause}} for cause in graph.get_node_ids()
        ]
        edges = []
        for cause in graph.get_nodes():
            for effect in cause.out_nodes:
                edges.append({"data": {"source": cause.id_, "target": effect.id_}})

        return nodes + edges
