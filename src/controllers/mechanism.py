from typing import Literal
from dash import MATCH, ALL, callback, Output, Input, State, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from views.mechanism import MechanismInput, RegressionBuilder, ClassificationBuilder

def setup_callbacks():
    @callback(
        Output({"type": "mechanism-input", "index": MATCH}, "children", allow_duplicate=True),
        Input({"type": "mechanism-choice", "index": MATCH}, "value"),
        State({"type": "mechanism-choice", "index": MATCH}, "id"),
        prevent_initial_call=True
    )
    def change_mechanism_type(choice: Literal["regression", "classification"], id: dict[str, str]):
        node = id.get("index", "")
        graph.get_node_by_id(node).change_mechanism(choice)
        if not node:
            raise PreventUpdate
        match choice:
            case "regression":
                return RegressionBuilder(node).children
            case "classification":
                return ClassificationBuilder(node).children
            case _:
                raise PreventUpdate

    @callback(
        Output({"type": "mechanism-input", "index": MATCH}, "children", allow_duplicate=True),
        Input({"type": "add-class", "index": MATCH}, "n_clicks"),
        State({"type": "add-class", "index": MATCH}, "id"),
        prevent_initial_call=True
    )
    def add_class(clicked, id: dict[str, str]):
        if not clicked:
            raise PreventUpdate
        node = id.get("index", "")
        mechanism = graph.get_node_by_id(node).mechanism
        if not mechanism.get_next_free_class_id():
            raise PreventUpdate
        mechanism.add_class()
        return MechanismInput(node).children
