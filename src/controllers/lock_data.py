import logging  # TODO: logging
import random
from time import sleep

from dash import Input, Output, State, callback, html, ctx
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
        Input("data-generation-store", "data"),
        prevent_initial_call=True,
    )
    def generate_data(should_train: bool):
        if not should_train:
            LockDataBuilder.is_locked = False
            LockDataBuilder.data_generated = False
            return (
                [],
                [],
                dbc.Row(
                    children=[
                        dbc.Col(LockDataBuilder(), width="10"),
                    ],
                    justify="center"
                ),
                False
            )

        global graph
        try:
            full_data_set = graph.generate_full_data_set()
            sleep(1.)
        except Exception as e:
            LockDataBuilder.is_locked = False
            LockDataBuilder.data_generated = False
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
        LockDataBuilder.is_locked = False
        LockDataBuilder.data_generated = True
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
        Output("global-reset-button", "disabled", allow_duplicate=True),
        Input("data-generation-store", "data"),
        prevent_initial_call=True
    )
    def toggle_ui_components(_):
        if ctx.triggered_id != "data-generation-store":
            raise PreventUpdate()

        match (LockDataBuilder.is_locked, LockDataBuilder.data_generated):
            case True, _:
                return (
                    True,
                    True,
                    True,
                    False,
                    True,
                    True,
                    True,
                    "tab-4",
                    True,
                )
            case False, True:
                return (
                    True,
                    True,
                    True,
                    False,
                    False,
                    False,
                    False,
                    "tab-4",
                    False,
                )
            case False, False:
                return (
                    False,
                    False,
                    False,
                    False,
                    True,
                    True,
                    True,
                    "tab-4",
                    False,
                )
            case _:
                print("this should not be possible")
                raise PreventUpdate()

    @callback(
        Output("data-generation-store", "data"),
        Input("lock-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def check_data_generation_prerequisites(clicked):
        if not clicked:
            raise PreventUpdate()

        if ctx.triggered_id != "lock-button":
            raise PreventUpdate()

        global graph
        LockDataBuilder.is_locked = True
        if LockDataBuilder.data_generated is True:
            LockDataBuilder.data_generated = False
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

