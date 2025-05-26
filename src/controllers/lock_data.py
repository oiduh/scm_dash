import logging  # TODO: logging
import random
from time import sleep

from dash import Input, Output, State, callback, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from models.graph import graph
from views.lock_data import LockDataBuilder
from views.data_summary import DataSummary, StaticGraph
from views.ml_prep import TrainingDataSetEditor



def setup_callbacks():
    @callback(
        Output("data-summary-container", "children", allow_duplicate=True),
        Output("training-data-set-editor", "children", allow_duplicate=True),
        Output("loading-4", "children", allow_duplicate=True),
        Output("data-generation-store", "data", allow_duplicate=True),
        Input("lock-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def generate_data(clicked):
        if not clicked:
            raise PreventUpdate()

        if LockDataBuilder.is_locked:
            return (
                DataSummary().children,
                TrainingDataSetEditor().children,
                dbc.Row(
                    children=[
                        dbc.Col(LockDataBuilder(), width="10"),
                    ],
                    justify="center"
                ),
                False
            )

        try:
            full_data_set = graph.generate_full_data_set()
            sleep(1.)
        except Exception as e:
            LockDataBuilder.is_locked = False
            return (
                DataSummary().children,
                TrainingDataSetEditor().children,
                dbc.Row(
                    children=[
                        dbc.Col(LockDataBuilder(True), width="10"),
                    ],
                    justify="center"
                ),
                False
            )

        graph.data = full_data_set
        LockDataBuilder.is_locked = True
        return (
            DataSummary().children,
            TrainingDataSetEditor().children,
            dbc.Row(
                children=[
                    dbc.Col(LockDataBuilder(), width="10"),
                ],
                justify="center"
            ),
            False
        )

    @callback(
        Output("tab1", "disabled", allow_duplicate=True),
        Output("tab2", "disabled", allow_duplicate=True),
        Output("tab3", "disabled", allow_duplicate=True),
        Output("tab4", "disabled", allow_duplicate=True),
        Output("tab5", "disabled", allow_duplicate=True),
        Output("tab6", "disabled", allow_duplicate=True),
        Output("tab7", "disabled", allow_duplicate=True),
        Output("tabs", "value", allow_duplicate=True),
        Input("data-generation-store", "data"),
        prevent_initial_call=True
    )
    def toggle_ui_components(is_loading: bool):
        if is_loading is True:
            return (
                True,
                True,
                True,
                False,
                True,
                True,
                True,
                "tab-4",
            )
        elif LockDataBuilder.is_locked:
            return (
                True,
                True,
                True,
                False,
                False,
                False,
                False,
                "tab-4",
            )
        else:
            return (
                False,
                False,
                False,
                False,
                True,
                True,
                True,
                "tab-4",
            )

    @callback(
        Output("data-generation-store", "data"),
        Input("lock-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def check_data_generation_prerequisites(clicked):
        if not clicked:
            raise PreventUpdate()

        if LockDataBuilder.is_locked is True:
            LockDataBuilder.is_locked = False
            graph.data = None
            StaticGraph.selected_node = None
            return False

        return True

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

