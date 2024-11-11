import logging

# from dash import ALL, Input, Output, State, callback, ctx
from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate
# from dash.exceptions import PreventUpdate

from models.graph import graph
from utils.logger import DashLogger
from views.graph import VariableConfig, VariableSelection, GraphViewer
# from views.mechanism import MechanismBuilder
# from views.noise import NoiseBuilder


LOGGER = DashLogger(name="GraphController", level=logging.DEBUG)

def get_graph_data():
    nodes = [
        {"data": {"id": cause, "label": cause}} for cause in graph.get_node_ids()
    ]
    edges = []
    for cause in graph.get_nodes():
        for effect in cause.out_nodes:
            edges.append({"data": {"source": cause.id_, "target": effect.id_}})
    return nodes + edges


def setup_callbacks() -> None:
    LOGGER.info("initializing graph callbacks")

    @callback(
        Output("variable-config", "children", allow_duplicate=True),
        Input("graph-builder-target-node", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def select_node(selected_node_id: str):
        LOGGER.info(f"selecting new node: {selected_node_id}")
        VariableSelection.selected_node_id = selected_node_id
        return VariableConfig().children

    @callback(
        Output("variable-selection", "children", allow_duplicate=True),
        Output("variable-config", "children", allow_duplicate=True),
        Output("network-graph", "elements", allow_duplicate=True),
        Input("add-new-node", "n_clicks"),
        prevent_initial_call="initial_duplicate",
    )
    def add_node(clicked):
        if not clicked:
            raise PreventUpdate()
        try:
            new_node_id = graph.add_node()
        except Exception as e:
            LOGGER.exception("Failed to add a new Node")
            raise PreventUpdate from e
        VariableSelection.selected_node_id = new_node_id

        return (
            VariableSelection().children,
            VariableConfig().children,
            get_graph_data()
        )

    @callback(
        Output("variable-selection", "children", allow_duplicate=True),
        Output("variable-config", "children", allow_duplicate=True),
        Output("network-graph", "elements", allow_duplicate=True),
        Input("remove-selected-node", "n_clicks"),
        State("graph-builder-target-node", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def remove_node(clicked, source_node_id: str):
        if not clicked:
            raise PreventUpdate()
        nodes = graph.get_nodes()
        if len(nodes) <= 1:
            raise PreventUpdate("at least one node must remain")
        try:
            node_to_remove = graph.get_node_by_id(source_node_id)
            assert node_to_remove
            graph.remove_node(node_to_remove)
        except Exception as e:
            LOGGER.error("Faield to remove an edge")
            raise PreventUpdate from e

        VariableSelection.selected_node_id = nodes[0].id_
        return(
            VariableSelection().children,
            VariableConfig().children,
            get_graph_data()
        )

    @callback(
        Output("variable-config", "children", allow_duplicate=True),
        Output("network-graph", "elements", allow_duplicate=True),
        Input("add-new-edge", "n_clicks"),
        State("graph-builder-target-node", "value"),
        State("add-out-node", "value"),
        prevent_initial_call="initial_duplicate",
    )
    def add_new_edge(clicked, source_node_id: str, target_node_id: str | None):
        if not clicked or target_node_id is None:
            raise PreventUpdate()

        source = graph.get_node_by_id(source_node_id)
        target = graph.get_node_by_id(target_node_id)
        if source is None or target is None:
            raise PreventUpdate()

        if source is None or target is None:
            LOGGER.error("Failed to find source and target node")
            raise PreventUpdate()

        try:
            graph.add_edge(source, target)
        except Exception as e:
            LOGGER.exception("Failed to add edge")
            raise PreventUpdate from e

        return (
            VariableConfig().children,
            get_graph_data()
        )

    @callback(
        Output("variable-config", "children", allow_duplicate=True),
        Output("network-graph", "elements", allow_duplicate=True),
        Input("remove-edge", "n_clicks"),
        State("graph-builder-target-node", "value"),
        State("remove-out-node", "value"),
        prevent_initial_call="initial_duplicate",
    )
    def remove_edge(clicked, source_node_id: str, target_node_id: str | None):
        if not clicked or target_node_id is None:
            raise PreventUpdate()

        source = graph.get_node_by_id(source_node_id)
        target = graph.get_node_by_id(target_node_id)

        if source is None or target is None:
            raise PreventUpdate()

        try:
            graph.remove_edge(source, target)
        except Exception as e:
            LOGGER.exception("Failed to add edge")
            raise PreventUpdate from e

        return (
            VariableConfig().children,
            get_graph_data()
        )

    @callback(
        Output("graph-viewer", "children"),
        Input("layout-choices", "value"),
    )
    def update_layout_choice(new_value: GraphViewer.Layouts):
        LOGGER.info("Updating graph viewer layout")
        LOGGER.info([x.id_ for x in graph.get_nodes()])
        if new_value not in GraphViewer.Layouts.get_all():
            raise PreventUpdate(f"Invalid layout choice: {new_value}")
        GraphViewer.LAYOUT = new_value
        return GraphViewer()

"""
    # TODO: old callbacks -> keep for reference
    @callback(
        Output("graph-builder", "children", allow_duplicate=True),
        Output("noise-builder", "children", allow_duplicate=True),
        Output("mechanism-builder", "children", allow_duplicate=True),
        Input("add-node-button", "n_clicks"),
        prevent_initial_call='initial_duplicate',
    )
    def add_node(clicked):
        if not clicked:
            # called on startup/refresh -> ensure last graph state restored
            return (
                GraphBuilder().children,
                NoiseBuilder().children,
                MechanismBuilder().children,
            )

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

    @callback(
        Output("network-graph", "elements"),
        Input("graph-builder", "children"),
    )
    def update_graph(*_):
        LOGGER.info("Updating graph view")
        nodes = [
            {"data": {"id": cause, "label": cause}} for cause in graph.get_node_ids()
        ]
        LOGGER.info(f"{nodes=}")
        edges = []
        for cause in graph.get_nodes():
            for effect in cause.out_nodes:
                edges.append({"data": {"source": cause.id_, "target": effect.id_}})

        return nodes + edges

    @callback(
        Output("graph-viewer", "children"),
        Input("layout-choices", "value"),
        prevent_initial_call=True,
    )
    def update_layout_choice(new_value: GraphViewer.Layouts):
        LOGGER.info("Updating graph viewer layout")
        LOGGER.info([x.id_ for x in graph.get_nodes()])
        if new_value not in GraphViewer.Layouts.get_all():
            raise PreventUpdate(f"Invalid layout choice: {new_value}")
        GraphViewer.LAYOUT = new_value
        return GraphViewer()
"""
