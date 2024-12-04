import logging

from dash import Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from models.mechanism import MechanismType
from utils.logger import DashLogger
from views.data_generation_summary import DataGenerationBuilder, DataGenerationViewer
from views.mechanism import (
    ClassificationBuilder,
    MechanismConfig,
    MechanismViewer,
    VariableSelection
)
def setup_callbacks():

    @callback(
        Output("data-generation-builder", "children", allow_duplicate=True),
        Input("lock-button", "n_clicks"),
        prevent_initial_call=True
    )
    def toggle_lock(clicked):
        if not clicked:
            raise PreventUpdate()

        # TODO: check if locking succeeds
        DataGenerationBuilder.is_locked = not DataGenerationBuilder.is_locked
        return DataGenerationBuilder().children

    @callback(
        Output("data-generation-viewer", "children", allow_duplicate=True),
        Input("layout-choices-data-generation", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def update_layout_choice(new_value: DataGenerationViewer.Layouts):
        if new_value not in DataGenerationViewer.Layouts.get_all():
            raise PreventUpdate(f"Invalid layout choice: {new_value}")
        DataGenerationViewer.LAYOUT = new_value
        # LOGGER.info(f"Updating graph viewer layout to: {new_value}")
        return DataGenerationViewer().children

    @callback(
        Output("data-generation-viewer", "children", allow_duplicate=True),
        Input("data-generation-graph-reset", "n_clicks"),
        prevent_initial_call="initial_duplicate"
    )
    def reset_graph(clicked):
        if not clicked:
            raise PreventUpdate()
        # LOGGER.info(f"Updating graph viewer layout to: {new_value}")
        return DataGenerationViewer().children
