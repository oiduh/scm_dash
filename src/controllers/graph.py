import string
import base64
import json
from typing import Any
import dataclasses

from dash import Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph, new_graph, Graph
from models.noise import GLOBAL_VARIABLES
from utils.logger import DashLogger
from views.graph import (
    GeneralGraphConfig,
    VariableConfig,
    VariableSelection as VariableSelectionGraph,
    GraphViewer,
    GraphBuilder,
    GraphUploader,
)
from views.ml_prep import MLViewer
from views.noise import NoiseBuilder, NoiseViewer, VariableSelection as VariableSelectionNoise
from views.mechanism import (
    MechanismBuilder,
    MechanismConfig,
    MechanismViewer,
    VariableSelection as VariableSelectionMechanism
)


LOGGER = DashLogger(name="Graph-Controller")


def setup_callbacks() -> None:
    LOGGER.info("initializing graph callbacks")

    @callback(
        Output("variable-selection-graph", "children", allow_duplicate=True),
        Output("variable-selection-noise", "children", allow_duplicate=True),
        Output("variable-selection-mechanism", "children", allow_duplicate=True),
        Output("variable-config-graph", "children", allow_duplicate=True),
        Input("graph-builder-target-node", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def select_node(selected_node_id: str):
        if selected_node_id == VariableSelectionGraph.selected_node_id:
            return (
                VariableSelectionGraph().children,
                VariableSelectionNoise().children,
                VariableSelectionMechanism().children,
                VariableConfig().children,
            )

        LOGGER.info(f"Selecting new node: {selected_node_id}")
        VariableSelectionGraph.selected_node_id = selected_node_id
        return (
            VariableSelectionGraph().children,
            VariableSelectionNoise().children,
            VariableSelectionMechanism().children,
            VariableConfig().children,
        )

    @callback(
        Output("variable-selection-graph", "children", allow_duplicate=True),
        Output("variable-config-graph", "children", allow_duplicate=True),
        Output("network-graph", "elements", allow_duplicate=True),
        Output("variable-selection-noise", "children", allow_duplicate=True),
        Output("mechanism-config", "children", allow_duplicate=True),
        Input("add-new-node", "n_clicks"),
        prevent_initial_call="initial_duplicate",
    )
    def add_node(clicked):
        if not clicked:
            raise PreventUpdate()
        try:
            new_node_id = graph.add_node()
        except Exception:
            LOGGER.exception("Failed to add a new Node")
            raise PreventUpdate()

        LOGGER.info(f"Added new node with id: {new_node_id}")
        VariableSelectionGraph.selected_node_id = new_node_id
        return (
            VariableSelectionGraph().children,
            VariableConfig().children,
            GraphBuilder.get_graph_data(),
            VariableSelectionNoise().children,
            MechanismConfig().children,
        )

    @callback(
        Output("variable-selection-graph", "children", allow_duplicate=True),
        Output("variable-config-graph", "children", allow_duplicate=True),
        Output("network-graph", "elements", allow_duplicate=True),
        Output("variable-selection-noise", "children", allow_duplicate=True),
        Output("mechanism-config", "children", allow_duplicate=True),
        Input("remove-selected-node", "n_clicks"),
        State("graph-builder-target-node", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def remove_node(clicked, source_node_id: str):
        if not clicked:
            raise PreventUpdate()

        nodes = graph.get_nodes()
        if len(nodes) == 1:
            LOGGER.error("Cannot remove last remaining node")
            raise PreventUpdate()
        try:
            node_to_remove = graph.get_node_by_id(source_node_id)
            assert node_to_remove is not None
            graph.remove_node(node_to_remove)
        except Exception:
            LOGGER.error("Failed to remove an edge")
            raise PreventUpdate

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
            MechanismConfig().children,
        )

    @callback(
        Output("variable-config-graph", "children", allow_duplicate=True),
        Output("network-graph", "elements", allow_duplicate=True),
        Output("mechanism-config", "children", allow_duplicate=True),
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
            LOGGER.error("The source and/or target node was not found")
            raise PreventUpdate()

        try:
            graph.add_edge(source, target)
        except Exception:
            LOGGER.exception("Failed to add edge")
            raise PreventUpdate

        LOGGER.info(f"Added edge from id={source_node_id} to id={target_node_id}")
        return (
            VariableConfig().children,
            GraphBuilder.get_graph_data(),
            MechanismConfig().children,
        )


    @callback(
        Output("variable-config-graph", "children", allow_duplicate=True),
        Output("network-graph", "elements", allow_duplicate=True),
        Output("mechanism-config", "children", allow_duplicate=True),
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
            LOGGER.error("Source and/or target node not found")
            raise PreventUpdate()

        try:
            graph.remove_edge(source, target)
        except Exception as e:
            LOGGER.exception("Failed to add edge")
            raise PreventUpdate from e

        LOGGER.info(f"Removed edge from id={source_node_id} to id={target_node_id}")
        return (
            VariableConfig().children,
            GraphBuilder.get_graph_data(),
            MechanismConfig().children,
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
        Output("noise-viewer", "children", allow_duplicate=True),
        Output("mechanism-config", "children", allow_duplicate=True),
        Input("confirm-new-name", "n_clicks"),
        State("variable-name", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def confirm_new_name(clicked, new_name: str | None):
        if not clicked or not new_name:
            raise PreventUpdate()

        if new_name[0] not in string.ascii_letters:
            LOGGER.error(f"First char must be ascii letter, found: '{new_name[0]}'")
            raise PreventUpdate()

        if len(new_name) == 1:
            LOGGER.error("Custom name must be longer than 1 char")
            raise PreventUpdate()

        if VariableSelectionGraph.selected_node_id is None:
            LOGGER.error("No variable selected")
            raise PreventUpdate()

        names_used = graph.get_node_names()
        if new_name in names_used:
            LOGGER.error(f"Name already used: {new_name}")
            raise PreventUpdate()

        node = graph.get_node_by_id(VariableSelectionGraph.selected_node_id)
        if node is None:
            LOGGER.fatal("Failed to find node")
            raise PreventUpdate()

        node.name = new_name
        LOGGER.info(f"Changed name for variable with id={node.id_}, from={node.name} to={new_name}")
        return (
            VariableSelectionGraph().children,
            VariableConfig().children,
            GraphBuilder.get_graph_data(),
            VariableSelectionNoise().children,
            NoiseViewer().children,
            MechanismConfig().children,
        )

    @callback(
        Output("graph-uploader", "children"),
        Input("graph-upload-field", "contents"),
        prevent_initial_call="initial_duplicate",
    )
    def check_uploaded_graph(content: str | None):
        if content is None:
            raise PreventUpdate()

        global graph, new_graph
        new_graph = None
        try:
            assert content is not None
            b64_str = content.rsplit(",", 1)[-1]
            graph_data: dict[str, Any] = json.loads(base64.b64decode(b64_str))
            new_graph = Graph.parse_from_dict(graph_data)
            GraphUploader.last_uploaded_graph = True
            LOGGER.info("Uploaded graph is OK")
        except Exception:
            GraphUploader.last_uploaded_graph = False
            LOGGER.exception("Uploaded graph is NOT OK")

        return GraphUploader().children

    @callback(
        Output("graph-builder-new", "children", allow_duplicate=True),
        Output("graph-viewer", "children", allow_duplicate=True),
        Output("noise-builder", "children", allow_duplicate=True),
        Output("noise-viewer", "children", allow_duplicate=True),
        Output("mechanism-builder", "children", allow_duplicate=True),
        Output("mechanism-viewer", "children", allow_duplicate=True),
        Output("ml-viewer", "children", allow_duplicate=True),
        Input("use-graph-button", "n_clicks"),
        prevent_initial_call="initial_duplicate",
    )
    def upload_graph(clicked):
        if not clicked:
            raise PreventUpdate()

        global graph, new_graph
        if new_graph is None:
            LOGGER.fatal("Cannot upload a graph that does not exist")
            raise PreventUpdate()

        for field in dataclasses.fields(Graph):
            setattr(graph, field.name, getattr(new_graph, field.name))

        new_graph = None

        GraphUploader.last_uploaded_graph = None
        VariableSelectionGraph.selected_node_id = None
        GraphViewer.LAYOUT = GraphViewer.Layouts.circle
        VariableSelectionMechanism.variable = None
        MechanismConfig.mechanism_type = None
        MechanismConfig.is_open = False

        LOGGER.info("New graph was uploaded and can be used")
        return (
            GraphBuilder().children,
            GraphViewer().children,
            NoiseBuilder().children,
            NoiseViewer().children,
            MechanismBuilder().children,
            MechanismViewer().children,
            MLViewer().children,
        )

    @callback(
        Output("general-graph-config", "children", allow_duplicate=True),
        Input("confirm-new-data-points", "n_clicks"),
        State("new-data-points", "value"),
        prevent_initial_call=True
    )
    def confirm_new_data_points(clicked, new_value):
        if not clicked or new_value is None:
            raise PreventUpdate()

        GLOBAL_VARIABLES.NR_DATA_POINTS = new_value
        LOGGER.info(f"Set new number of data points to: {new_value}")
        return GeneralGraphConfig().children

    @callback(
        Output("general-graph-config", "children", allow_duplicate=True),
        Input("confirm-new-seed", "n_clicks"),
        State("new-seed", "value"),
        prevent_initial_call=True
    )
    def confirm_new_seed(clicked, new_value):
        if not clicked or new_value is None:
            raise PreventUpdate()

        GLOBAL_VARIABLES.SEED = new_value if new_value is not None else 42
        LOGGER.info(f"Set new seed to: {new_value}")
        return GeneralGraphConfig().children

    @callback(
        Output("general-graph-config", "children"),
        Input("random-seed-check", "value"),
        State("new-seed", "value"),
        prevent_initial_call=True
    )
    def toggle_seed_mode(new_mode, current_value):
        print(f"{current_value=}")
        match new_mode:
            case "fixed":
                GLOBAL_VARIABLES.SEED = 42 if current_value is None else GLOBAL_VARIABLES.SEED
            case "random":
                GLOBAL_VARIABLES.SEED = None
            case _:
                LOGGER.error(f"unknown seed mode detected: {new_mode}")
                raise PreventUpdate()

        GeneralGraphConfig.seed_mode = new_mode
        return GeneralGraphConfig().children
