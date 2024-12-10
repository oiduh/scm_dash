import logging

from dash import Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from models.mechanism import MechanismType
from utils.logger import DashLogger
from views.lock_data import LockDataBuilder, LockDataViewer
from views.data_summary import DataSummaryViewer



def setup_callbacks():

    @callback(
        Output("data-generation-builder", "children", allow_duplicate=True),
        Output("tab1", "disabled"),
        Output("tab2", "disabled"),
        Output("tab3", "disabled"),
        Output("tab5", "disabled"),
        Output("data-generation-viewer", "children", allow_duplicate=True),
        Output("data-summary-viewer", "children", allow_duplicate=True),
        Input("lock-button", "n_clicks"),
        prevent_initial_call=True
    )
    def toggle_lock(clicked):
        if not clicked:
            raise PreventUpdate()
        if LockDataBuilder.is_locked:
            LockDataBuilder.is_locked = not LockDataBuilder.is_locked
            LockDataViewer.error = False
            graph.data = None
            return (
                LockDataBuilder().children,
                False,
                False,
                False,
                True,
                LockDataViewer().children,
                DataSummaryViewer().children,
            )

        try:
            full_data_set = graph.generate_full_data_set()
        except Exception as e:
            LockDataViewer.error = True
            graph.data = None
            return (
                LockDataBuilder().children,
                False,
                False,
                False,
                True,
                LockDataViewer().children,
                DataSummaryViewer().children,
            )

        graph.data = full_data_set

        # TODO: check if locking succeeds
        LockDataBuilder.is_locked = not LockDataBuilder.is_locked
        LockDataViewer.error = False
        return (
            LockDataBuilder().children,
            True,
            True,
            True,
            False,
            LockDataViewer().children,
            DataSummaryViewer().children,
        )

