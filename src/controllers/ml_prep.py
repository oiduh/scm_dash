import logging
import json

from dash import ALL, Input, Output, State, callback
from dash.exceptions import PreventUpdate

from models.graph import graph
from utils.logger import DashLogger
from views.data_summary import DataSummaryViewer, NodeViewer
from views.graph import GraphBuilder
from views.ml_prep import MLPreparation, TrainingDataSetEditor


# TODO: add logs to functions
LOGGER = DashLogger(name="MLPrep", level=logging.DEBUG)


def setup_callbacks() -> None:
    LOGGER.info("initializing ml prep callbacks")

    @callback(
        Output("ml-preparation", "children", allow_duplicate=True),
        Input("add-training-set", "n_clicks"),
        prevent_initial_call="initial_duplicate"
    )
    def add_data_set(clicked):
        if not clicked:
            raise PreventUpdate()
        print("clicked add data set")
        if TrainingDataSetEditor.active is True:
            raise PreventUpdate()

        TrainingDataSetEditor.active = True
        return MLPreparation().children

    @callback(
        Output("ml-preparation", "children", allow_duplicate=True),
        Input("remove-training-set", "n_clicks"),
        prevent_initial_call="initial_duplicate"
    )
    def remove_data_set(clicked):
        if not clicked:
            raise PreventUpdate()
        assert TrainingDataSetEditor.active is True
        TrainingDataSetEditor.active = False
        return MLPreparation().children

    @callback(
        Output("ml-preparation", "children", allow_duplicate=True),
        Input("save-training-set", "n_clicks"),
        State({ "type": "selected-source-id", "index": ALL}, "id"),
        State({ "type": "selected-source-id", "index": ALL}, "value"),
        State("selected-target-id", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def save_data_set(clicked, source_ids: list[dict[str, str]], source_values: list[bool], target_id: str):
        if not clicked or TrainingDataSetEditor.active is False:
            raise PreventUpdate()

        variables = [x.get("index", "") for x in source_ids]
        if len(set(variables)) != len(source_ids):
            raise PreventUpdate()

        source_id_dict = {
            id: value for id, value in zip(variables, source_values)
        }
        if target_id not in source_id_dict or source_id_dict.get(target_id) is True:
            raise PreventUpdate()

        selected_sources = {k for k, v in source_id_dict.items() if v is True}
        if len(selected_sources) == 0:
            raise PreventUpdate()

        if graph.add_data_set(source_id_dict) is False:
            raise PreventUpdate()

        TrainingDataSetEditor.active = False
        return MLPreparation().children

    @callback(
        Output("ml-preparation", "children", allow_duplicate=True),
        Input("selected-target-id", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def select_new_target(new_value: str):
        if new_value == TrainingDataSetEditor.target_id:
            raise PreventUpdate()

        assert TrainingDataSetEditor.active is True
        TrainingDataSetEditor.target_id = new_value
        return MLPreparation().children
