import logging

# from dash import ALL, Input, Output, State, callback, ctx
from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate
# from dash.exceptions import PreventUpdate

from models.graph import graph
from utils.logger import DashLogger
from views.graph import VariableConfig, VariableSelection, GraphViewer, GraphBuilder
# from views.mechanism import MechanismBuilder
# from views.noise import NoiseBuilder


LOGGER = DashLogger(name="GraphController", level=logging.DEBUG)


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
            GraphBuilder.get_graph_data()
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
            GraphBuilder.get_graph_data()
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
            GraphBuilder.get_graph_data()
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
            GraphBuilder.get_graph_data()
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

    # @callback(
    #     Output(),
    #     Input(),
    #     State()
    # )
    # def confirm_new_name():
    #     pass
