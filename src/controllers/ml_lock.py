import random
import logging
from dash import callback, Output, Input
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

from models.graph import graph
from views.ml_lock import MLLockBuilder
from views.ml_result import MLResultViewer

def setup_callbacks():
    @callback(
        Output("ml-result-viewer", "children", allow_duplicate=True),
        Output("loading-7", "children", allow_duplicate=True),
        Output("ml-prep-store", "data", allow_duplicate=True),
        Input("ml-lock-button", "n_clicks"),
        prevent_initial_call=True
    )
    def toggle_lock(clicked):
        # TODO: when we lock, we should also start running the ml algos
        # since it might take longer: progress bar for each algo
        # lock all previous tabs
        # maybe add a stop button to stop all algos with no results
        if not clicked:
            raise PreventUpdate()
        if MLLockBuilder.is_locked:
            MLLockBuilder.is_locked = not MLLockBuilder.is_locked
            return (
                [],
                dbc.Row(
                    children=[
                        dbc.Col(MLLockBuilder(), width="10")
                    ],
                    justify="center"
                ),
                False
            )
        global graph
        if len(graph.data_sets) == 0:
            return (
                [],
                dbc.Row(
                    children=[
                        dbc.Col(MLLockBuilder(True), width="10")
                    ],
                    justify="center"
                ),
                False
            )

        try:
            # TODO: should be a cancellable job via button?
            print("running all ml algos...")
        except Exception as e:
            return (
                [],
                dbc.Row(
                    children=[
                        dbc.Col(MLLockBuilder(), width="10")
                    ],
                    justify="center"
                ),
                False
            )

        MLLockBuilder.is_locked = not MLLockBuilder.is_locked
        return (
            MLResultViewer().children,
            dbc.Row(
                children=[
                    dbc.Col(MLLockBuilder(), width="10")
                ],
                justify="center"
            ),
            True
        )

    @callback(
        Output("tab4", "disabled"),
        Output("tab5", "disabled"),
        Output("tab6", "disabled"),
        Output("tab7", "disabled"),
        Output("tab8", "disabled"),
        Output("tabs", "value"),
        Input("ml-prep-store", "data"),
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
                "tab-7",
            )
        elif MLLockBuilder.is_locked:
            return (
                True,
                False,
                True,
                False,
                False,
                "tab-7",
            )
        else:
            return (
                False,
                False,
                False,
                False,
                True,
                "tab-7",
            )

    @callback(
        Output("ml-prep-store", "data"),
        Input("ml-lock-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def check_ml_train_prerequisites(clicked):
        if not clicked:
            raise PreventUpdate()

        if MLLockBuilder.is_locked is True:
            MLLockBuilder.is_locked = False
            return False

        return True

    @callback(
        Output("export-graph-text-ml", "data"),
        Input("export-graph-ml", "n_clicks"),
        prevent_initial_call=True
    )
    def export_data(clicked):
        if not clicked:
            raise PreventUpdate()
        return {
            "content": graph.to_dict(),
            "filename": f"graph_{random.randint(1000,9999)}.txt"
        }

