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
