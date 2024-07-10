from typing import Literal

from dash import ALL, MATCH, Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from views.mechanism import (
    ClassificationBuilder,
    MechanismBuilder,
    MechanismInput,
    RegressionBuilder,
)


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

        node = graph.get_node_by_id(node_id)
        if node is None:
            raise PreventUpdate("Node not found")

        node.change_mechanism_type(choice)
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
            print(1)
            raise PreventUpdate
        node_id = id.get("index", None)
        if node_id is None:
            print(2)
            raise PreventUpdate("Node id not found")

        node = graph.get_node_by_id(node_id)
        if node is None:
            print(3)
            raise PreventUpdate("Node not found")

        mechanism = node.mechanism_metadata
        if mechanism.get_next_free_class_id() is None:
            print(4)
            raise PreventUpdate

        try:
            mechanism.add_class()
        except Exception as e:
            print(5)
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
        node = graph.get_node_by_id(node_id)
        if node is None:
            raise PreventUpdate("Node not found")

        mechanism = node.mechanism_metadata
        if mechanism.get_class_by_id(class_id) is None:
            raise PreventUpdate

        try:
            mechanism.remove_class(class_id)
        except Exception as e:
            raise PreventUpdate from e

        return MechanismBuilder().children
