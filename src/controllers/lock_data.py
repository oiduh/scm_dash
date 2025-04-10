import logging  # TODO: logging
import random

from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from pandas.io.formats.printing import justify

from models.graph import graph
from views.lock_data import LockDataBuilder
from views.data_summary import DataSummary, DataSummaryViewer, StaticGraph
from views.ml_prep import MLPreparation



def setup_callbacks():
    @callback(
        Output("tab1", "disabled", allow_duplicate=True),
        Output("tab2", "disabled", allow_duplicate=True),
        Output("tab3", "disabled", allow_duplicate=True),
        Output("tab4", "disabled", allow_duplicate=True),
        Output("tab5", "disabled", allow_duplicate=True),
        Output("tab6", "disabled", allow_duplicate=True),
        Output("tab7", "disabled", allow_duplicate=True),
        Output("data-summary-container", "children", allow_duplicate=True),
        Output("ml-preparation", "children", allow_duplicate=True),
        Output("loading-4", "children", allow_duplicate=True),
        Output("tabs", "value", allow_duplicate=True),
        Input("lock-button", "n_clicks"),
        prevent_initial_call=True
    )
    def toggle_lock(clicked):
        if not clicked:
            raise PreventUpdate()
        if LockDataBuilder.is_locked:
            # unlock data and reset class variables
            LockDataBuilder.is_locked = not LockDataBuilder.is_locked
            graph.data = None
            StaticGraph.selected_node = None
            return (
                False,
                False,
                False,
                False,
                True,
                True,
                True,
                DataSummary().children,
                MLPreparation().children,
                dbc.Row(
                    children=[
                        dbc.Col(LockDataBuilder(), width="10"),
                    ],
                    justify="center"
                ),
                "tab-4"
            )

        try:
            full_data_set = graph.generate_full_data_set()
        except Exception as e:
            graph.data = None
            return (
                False,
                False,
                False,
                False,
                True,
                True,
                True,
                DataSummary().children,
                MLPreparation().children,
                dbc.Row(
                    children=[
                        dbc.Col(LockDataBuilder(True), width="10"),
                    ],
                    justify="center"
                ),
                "tab-4"
            )

        graph.data = full_data_set

        LockDataBuilder.is_locked = not LockDataBuilder.is_locked

        return (
            True,
            True,
            True,
            False,
            False,
            False,
            False,
            DataSummary().children,
            MLPreparation().children,
            dbc.Row(
                children=[
                    dbc.Col(LockDataBuilder(), width="10"),
                ],
                justify="center"
            ),
            "tab-4"
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

