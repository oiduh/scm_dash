from typing import Literal
from dash import MATCH, ALL, callback, Output, Input, State, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from views.mechanism import RegressionBuilder, ClassificationBuilder

def setup_callbacks():
    @callback(
        Output({"type": "mechanism-input", "index": MATCH}, "children"),
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
            case "Regression":
                return RegressionBuilder(node).children
            case "Classification":
                return ClassificationBuilder(node).children
            case _:
                raise PreventUpdate
