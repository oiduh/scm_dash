import logging
from typing import Literal

from dash import ALL, MATCH, Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from utils.logger import DashLogger
from views.mechanism import (
    ClassificationBuilder,
    MechanismBuilder,
    MechanismInput,
    RegressionBuilder,
)

LOGGER = DashLogger(name="MechanismController", level=logging.DEBUG)


def setup_callbacks():
    @callback(
        Output(
            {"type": "mechanism-input", "index": MATCH},
            "children",
            allow_duplicate=True,
        ),
        Input({"type": "mechanism-choice", "index": MATCH}, "value"),
        State({"type": "mechanism-choice", "index": MATCH}, "id"),
        prevent_initial_call=True,
    )
    def change_mechanism_type(
        choice: Literal["regression", "classification"], id_: dict[str, str]
    ):
        if choice not in ["regression", "classification"]:
            raise PreventUpdate("Invalid choice")

        node_id = id_.get("index", None)
        if node_id is None:
            raise PreventUpdate("Node not found")

        LOGGER.info(f"Invoked 'change_mechanism_type' for node with id: {node_id}")

        node = graph.get_node_by_id(node_id)
        if node is None:
            LOGGER.error(f"Failed to find node with id: {node_id}")
            raise PreventUpdate("Node not found")

        node.change_type(choice)
        if choice == "regression":
            return RegressionBuilder(node_id).children
        else:
            return ClassificationBuilder(node_id).children

    @callback(
        Output(
            {"type": "mechanism-input", "index": MATCH},
            "children",
            allow_duplicate=True,
        ),
        Input({"type": "add-class", "index": MATCH}, "n_clicks"),
        State({"type": "add-class", "index": MATCH}, "id"),
        prevent_initial_call=True,
    )
    def add_class(clicked, id: dict[str, str]):
        if not clicked:
            raise PreventUpdate

        node_id = id.get("index", None)
        if node_id is None:
            raise PreventUpdate("Node id not found")

        LOGGER.info(f"Invoked 'add_class' for node with id: {node_id}")

        node = graph.get_node_by_id(node_id)
        if node is None:
            LOGGER.error(f"Failed to find node with id: {node_id}")
            raise PreventUpdate("Node not found")

        mechanism = node.mechanism_metadata
        if mechanism.get_next_free_class_id() is None:
            LOGGER.error("Max limit of sub classes reached")
            raise PreventUpdate

        try:
            mechanism.add_class()
        except Exception as e:
            LOGGER.exception("Failed to add class")
            raise PreventUpdate from e

        return MechanismInput(node_id).children

    @callback(
        Output("mechanism-builder", "children", allow_duplicate=True),
        Input({"type": "remove-class", "index": ALL}, "n_clicks"),
        State({"type": "remove-class", "index": ALL}, "id"),
        prevent_initial_call=True,
    )
    def remove_class(clicked, id: dict[str, str]):
        if not any(clicked):
            raise PreventUpdate

        triggered_node: dict | None = ctx.triggered_id
        if triggered_node is None:
            raise PreventUpdate

        index = triggered_node.get("index", None)
        if index is None:
            raise PreventUpdate

        node_id, class_id = index.split("_")

        LOGGER.info(f"Invoked 'remove_class' for node with id: {node_id}_{class_id}")

        node = graph.get_node_by_id(node_id)
        if node is None:
            LOGGER.error(f"Failed to find node with id: {node_id}")
            raise PreventUpdate("Node not found")

        mechanism = node.mechanism_metadata
        if mechanism.get_class_by_id(class_id) is None:
            LOGGER.error(f"Failed to find class with id: {class_id}")
            raise PreventUpdate

        try:
            mechanism.remove_class(class_id)
        except Exception as e:
            LOGGER.exception(f"Failed to remove class")
            raise PreventUpdate from e

        return MechanismBuilder().children
