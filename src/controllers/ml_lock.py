import logging
from dash import callback, Output, Input
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from pandas.io.formats.printing import justify

from views.ml_lock import MLLockBuilder
from views.ml_result import MLResultViewer

def setup_callbacks():
    @callback(
        Output("ml-result-viewer", "children", allow_duplicate=True),
        Output("tab4", "disabled"),
        Output("tab5", "disabled"),
        Output("tab6", "disabled"),
        Output("tab8", "disabled"),
        Output("tabs", "value"),
        Output("loading-7", "children"),
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
                False,
                False,
                False,
                True,
                "tab-7",
                dbc.Row(
                    children=[
                        dbc.Col(MLLockBuilder().children, width="10")
                    ],
                    justify="center"
                ),
            )

        try:
            # TODO: should be a cancellable job via button?
            print("running all ml algos...")
        except Exception as e:
            return (
                [],
                False,
                False,
                False,
                True,
                "tab-7",
                dbc.Row(
                    children=[
                        dbc.Col(MLLockBuilder().children, width="10")
                    ],
                    justify="center"
                ),
            )

        MLLockBuilder.is_locked = not MLLockBuilder.is_locked
        return (
            MLResultViewer().children,
            True,
            False,
            True,
            False,
            "tab-7",
            dbc.Row(
                children=[
                    dbc.Col(MLLockBuilder().children, width="10")
                ],
                justify="center"
            ),
        )
