import logging

from dash import ALL, Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from utils.logger import DashLogger
from views.graph import GraphBuilder
from views.mechanism import MechanismBuilder
from views.noise import NoiseBuilder

LOGGER = DashLogger(name="GraphController", level=logging.DEBUG)


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

        LOGGER.info("invoked 'add_node'")

        try:
            graph.add_node()
        except Exception as e:
            LOGGER.exception("Failed to add a new Node")
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
        if any(clicked) is False:
            raise PreventUpdate

        LOGGER.info("invoked 'remove_node'")

        triggered_node: dict | None = ctx.triggered_id
        if not triggered_node or (node_id := triggered_node.get("index")) is None:
            LOGGER.error(f"Wrong node triggered: {triggered_node}")
            raise PreventUpdate

        node = graph.get_node_by_id(node_id)
        if node is None:
            LOGGER.error(f"Did not find node with id {node_id}")
            raise PreventUpdate

        try:
            graph.remove_node(node)
        except Exception as e:
            LOGGER.exception(f"Failed to remove node with id {node_id}")
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
    def add_edge(clicked, choices, ids):
        if any(clicked) is False:
            raise PreventUpdate

        LOGGER.info("invoked 'add_edge'")

        context: dict | None = ctx.triggered_id
        if context is None:
            LOGGER.error("Wrong context")
            raise PreventUpdate

        source_node_id: str | None = context.get("index")
        if source_node_id is None:
            LOGGER.error(f"Failed to find source node with id: {source_node_id}")
            raise PreventUpdate

        index = [x.get("index") for x in ids].index(source_node_id)
        target_node_id = choices[index]
        if target_node_id is None:
            LOGGER.error(f"Failed to find target node with id: {source_node_id}")
            raise PreventUpdate

        source = graph.get_node_by_id(source_node_id)
        target = graph.get_node_by_id(target_node_id)

        if source is None or target is None:
            LOGGER.error("Failed to find source and target node")
            raise PreventUpdate

        try:
            graph.add_edge(source, target)
        except Exception as e:
            LOGGER.exception("Failed to add edge")
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
    def remove_edge(clicked, choices, ids):
        if any(clicked) is False:
            raise PreventUpdate

        LOGGER.info("invoked 'remove_edge'")

        context: dict | None = ctx.triggered_id
        if context is None:
            LOGGER.error("Wrong context")
            raise PreventUpdate

        source_node_id: str | None = context.get("index")
        if source_node_id is None:
            LOGGER.error(f"Failed to find source node with id: {source_node_id}")
            raise PreventUpdate

        index = [x.get("index") for x in ids].index(source_node_id)
        target_node_id = choices[index]
        if target_node_id is None:
            LOGGER.error(f"Failed to find target node with id: {source_node_id}")
            raise PreventUpdate

        source = graph.get_node_by_id(source_node_id)
        target = graph.get_node_by_id(target_node_id)

        if source is None or target is None:
            LOGGER.error("Failed to find source and target node")
            raise PreventUpdate
        try:
            graph.remove_edge(source, target)
        except Exception as e:
            LOGGER.exception("Failed to remove edge")
            raise PreventUpdate from e

        return GraphBuilder().children, MechanismBuilder().children

    @callback(Output("network-graph", "elements"), Input("graph-builder", "children"))
    def update_graph(*_):
        LOGGER.info("Updating graph view")
        nodes = [
            {"data": {"id": cause, "label": cause}} for cause in graph.get_node_ids()
        ]
        edges = []
        for cause in graph.get_nodes():
            for effect in cause.out_nodes:
                edges.append({"data": {"source": cause.id_, "target": effect.id_}})

        return nodes + edges
