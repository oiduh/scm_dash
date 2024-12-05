import logging

from dash import Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from models.mechanism import MechanismType
from utils.logger import DashLogger
from views.data_generation_summary import DataGenerationBuilder
from views.mechanism import (
    ClassificationBuilder,
    MechanismConfig,
    MechanismViewer,
    VariableSelection
)
def setup_callbacks():

    @callback(
        Output("data-generation-builder", "children", allow_duplicate=True),
        Output("tab1", "disabled"),
        Output("tab2", "disabled"),
        Output("tab3", "disabled"),
        Output("tab5", "disabled"),
        Input("lock-button", "n_clicks"),
        prevent_initial_call=True
    )
    def toggle_lock(clicked):
        if not clicked:
            raise PreventUpdate()
        if DataGenerationBuilder.is_locked:
            DataGenerationBuilder.is_locked = not DataGenerationBuilder.is_locked
            return (
                DataGenerationBuilder().children,
                False,
                False,
                False,
                True,
            )

        try:
            full_data_set = graph.generate_full_data_set()
        except Exception as e:
            print(e)
            raise PreventUpdate from e

        print(full_data_set)

        # TODO: check if locking succeeds
        DataGenerationBuilder.is_locked = not DataGenerationBuilder.is_locked
        return (
            DataGenerationBuilder().children,
            True,
            True,
            True,
            False,
        )

