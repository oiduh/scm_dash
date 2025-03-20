import logging
import random

from dash import Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from models.mechanism import MechanismType
from utils.logger import DashLogger
from views.lock_data import LockDataBuilder, LockDataViewer
from views.data_summary import DataSummaryViewer
from views.ml_prep import MLPreparation



def setup_callbacks():
    @callback(
        Output("data-generation-builder", "children", allow_duplicate=True),
        Output("tab1", "disabled", allow_duplicate=True),
        Output("tab2", "disabled", allow_duplicate=True),
        Output("tab3", "disabled", allow_duplicate=True),
        Output("tab5", "disabled", allow_duplicate=True),
        Output("tab6", "disabled", allow_duplicate=True),
        Output("tab7", "disabled", allow_duplicate=True),
        Output("tab8", "disabled", allow_duplicate=True),
        Output("data-generation-viewer", "children", allow_duplicate=True),
        Output("data-summary-viewer", "children", allow_duplicate=True),
        Output("ml-preparation", "children", allow_duplicate=True),
        Output("loading-output-1", "children", allow_duplicate=True),
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
                True,
                True,
                True,
                LockDataViewer().children,
                DataSummaryViewer().children,
                MLPreparation().children,
                []
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
                True,
                True,
                True,
                LockDataViewer().children,
                DataSummaryViewer().children,
                MLPreparation().children,
                [],
            )

        graph.data = full_data_set

        LockDataBuilder.is_locked = not LockDataBuilder.is_locked
        LockDataViewer.error = False
        import time
        time.sleep(3)
        return (
            LockDataBuilder().children,
            True,
            True,
            True,
            False,
            False,
            False,
            True,
            LockDataViewer().children,
            DataSummaryViewer().children,
            MLPreparation().children,
            [],
        )

    @callback(
        Output("export-graph-text", "data"),
        Input("export-graph", "n_clicks"),
        prevent_initial_call=True
    )
    def export_data(clicked):
        if not clicked:
            raise PreventUpdate()
        return {
            "content": graph.to_dict(),
            "filename": f"graph_{random.randint(1000,9999)}.txt"
        }

