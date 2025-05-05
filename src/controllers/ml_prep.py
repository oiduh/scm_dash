import logging

from dash import ALL, Input, Output, State, callback
from dash.exceptions import PreventUpdate

from models.graph import graph
from utils.logger import DashLogger
from views.ml_prep import MLViewer, TrainingDataSetEditor


# TODO: add logs to functions
LOGGER = DashLogger(name="MLPrep", level=logging.DEBUG)


def setup_callbacks() -> None:
    LOGGER.info("initializing ml prep callbacks")

    @callback(
        Output("training-data-set-editor", "children", allow_duplicate=True),
        Output("ml-viewer", "children", allow_duplicate=True),
        Input("save-training-set", "n_clicks"),
        State("selected-source-ids", "value"),
        State("selected-target-id", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def save_data_set(clicked, source_ids: list[str], target_id: str):
        if not clicked:
            raise PreventUpdate()

        if len(source_ids) < 1:
            raise PreventUpdate()

        source_id_dict = {id_: True for id_ in source_ids}
        if graph.add_data_set(source_id_dict, target_id) is False:
            raise PreventUpdate()

        return (
            TrainingDataSetEditor().children,
            MLViewer().children,
        )

    @callback(
        Output("training-data-set-editor", "children", allow_duplicate=True),
        Input("selected-target-id", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def select_new_target(new_value: str):
        if new_value == TrainingDataSetEditor.target_id:
            raise PreventUpdate()

        TrainingDataSetEditor.target_id = new_value
        return TrainingDataSetEditor().children

    @callback(
        Output("ml-viewer", "children", allow_duplicate=True),
        Input({ "type": "remove-data-set", "index": ALL}, "n_clicks"),
        prevent_initial_call="initial_duplicate"
    )
    def remove_data_set_viewer(remove_buttons: list):
        if not any(remove_buttons):
            raise PreventUpdate()
        index = remove_buttons.index(next(x for x in remove_buttons if x))
        graph.data_sets.pop(index)
        return MLViewer().children
