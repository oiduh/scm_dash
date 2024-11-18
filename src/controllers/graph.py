import logging
import string

# from dash import ALL, Input, Output, State, callback, ctx
from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate
from scipy.stats import distributions
# from dash.exceptions import PreventUpdate

from models.graph import graph
from utils.logger import DashLogger
from views.graph import (
    VariableConfig,
    VariableSelection as VariableSelectionGraph,
    GraphViewer,
    GraphBuilder,
)
from views.noise import VariableSelection as VariableSelectionNoise
# from views.mechanism import MechanismBuilder


LOGGER = DashLogger(name="GraphController", level=logging.DEBUG)


def setup_callbacks() -> None:
    LOGGER.info("initializing graph callbacks")

    @callback(
        Output("variable-config-graph", "children", allow_duplicate=True),
        Input("graph-builder-target-node", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def select_node(selected_node_id: str):
        if selected_node_id == VariableSelectionGraph.selected_node_id:
            # just in case
            raise PreventUpdate()

        LOGGER.info(f"Selecting new node: {selected_node_id}")
        VariableSelectionGraph.selected_node_id = selected_node_id
        return VariableConfig().children

    @callback(
        Output("variable-selection-graph", "children", allow_duplicate=True),
        Output("variable-config-graph", "children", allow_duplicate=True),
        Output("network-graph", "elements", allow_duplicate=True),
        Output("variable-selection-noise", "children", allow_duplicate=True),
        Input("add-new-node", "n_clicks"),
        prevent_initial_call="initial_duplicate",
    )
    def add_node(clicked):
        if not clicked:
            raise PreventUpdate()
        try:
            new_node_id = graph.add_node()
            LOGGER.info(f"Added new node with id: {new_node_id}")
        except Exception as e:
            LOGGER.exception("Failed to add a new Node")
            raise PreventUpdate from e
        VariableSelectionGraph.selected_node_id = new_node_id

        return (
            VariableSelectionGraph().children,
            VariableConfig().children,
            GraphBuilder.get_graph_data(),
            VariableSelectionNoise().children,
        )

    @callback(
        Output("variable-selection-graph", "children", allow_duplicate=True),
        Output("variable-config-graph", "children", allow_duplicate=True),
        Output("network-graph", "elements", allow_duplicate=True),
        Output("variable-selection-noise", "children", allow_duplicate=True),
        Input("remove-selected-node", "n_clicks"),
        State("graph-builder-target-node", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def remove_node(clicked, source_node_id: str):
        if not clicked:
            raise PreventUpdate()

        nodes = graph.get_nodes()
        if len(nodes) == 1:
            raise PreventUpdate("at least one node must remain")
        try:
            node_to_remove = graph.get_node_by_id(source_node_id)
            assert node_to_remove
            graph.remove_node(node_to_remove)
        except Exception as e:
            LOGGER.error("Faield to remove an edge")
            raise PreventUpdate from e

        nodes = graph.get_nodes()  # get updated nodes
        new_selection = nodes[0]
        VariableSelectionGraph.selected_node_id = new_selection.id_
        if node_to_remove.id_ == VariableSelectionNoise.variable:
            VariableSelectionNoise.variable = new_selection.id_
            distribution = new_selection.noise.get_distributions()[0]
            VariableSelectionNoise.sub_variable = distribution.id_

        LOGGER.info(f"Removed node with id: {source_node_id}")
        return(
            VariableSelectionGraph().children,
            VariableConfig().children,
            GraphBuilder.get_graph_data(),
            VariableSelectionNoise().children,
        )

    @callback(
        Output("variable-config-graph", "children", allow_duplicate=True),
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

        LOGGER.info(f"Added edge from id={source_node_id} to id={target_node_id}")
        return (
            VariableConfig().children,
            GraphBuilder.get_graph_data()
        )

    @callback(
        Output("variable-config-graph", "children", allow_duplicate=True),
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

        LOGGER.info(f"Removed edge from id={source_node_id} to id={target_node_id}")
        return (
            VariableConfig().children,
            GraphBuilder.get_graph_data()
        )

    @callback(
        Output("graph-viewer", "children"),
        Input("layout-choices", "value"),
    )
    def update_layout_choice(new_value: GraphViewer.Layouts):
        if new_value not in GraphViewer.Layouts.get_all():
            raise PreventUpdate(f"Invalid layout choice: {new_value}")
        GraphViewer.LAYOUT = new_value
        LOGGER.info(f"Updating graph viewer layout to: {new_value}")
        return GraphViewer().children

    @callback(
        Output("variable-selection-graph", "children", allow_duplicate=True),
        Output("variable-config-graph", "children", allow_duplicate=True),
        Output("network-graph", "elements", allow_duplicate=True),
        Output("variable-selection-noise", "children", allow_duplicate=True),
        Input("confirm-new-name", "n_clicks"),
        State("variable-name", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def confirm_new_name(clicked, new_name: str | None):
        if not clicked or not new_name:
            raise PreventUpdate()

        if new_name[0] not in string.ascii_letters:
            LOGGER.warning(f"First char must be ascii letter, found: '{new_name[0]}'")
            raise PreventUpdate()

        if len(new_name) == 1:
            LOGGER.warning("Custom name must be longer than 1 char")
            raise PreventUpdate()

        if VariableSelectionGraph.selected_node_id is None:
            LOGGER.error("No variable selected")
            raise PreventUpdate()

        names_used = graph.get_node_names()
        if new_name in names_used:
            LOGGER.warning(f"Name already used: {new_name}")
            raise PreventUpdate()

        node = graph.get_node_by_id(VariableSelectionGraph.selected_node_id)
        assert node is not None

        LOGGER.warning(f"Changed name for variable with id={node.id_}, from={node.name} to={new_name}")
        node.name = new_name
        return (
            VariableSelectionGraph().children,
            VariableConfig().children,
            GraphBuilder.get_graph_data(),
            VariableSelectionNoise().children
        )
