import random
import logging
from dash import callback, Output, Input, State, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
from uuid import uuid4

from models.graph import graph
from models.mechanism import MechanismType
from models.ml import Classification, Regression, SelfTrainingClassification, SemiSupervisedClassification
from views.ml_lock import MLLockBuilder
from views.ml_result import MLResultViewer

def setup_callbacks():
    @callback(
        Output("ml-result-viewer", "children", allow_duplicate=True),
        Output("loading-7", "children", allow_duplicate=True),
        Output("ml-lock-store", "data", allow_duplicate=True),
        Input("ml-lock-store", "data"),
        prevent_initial_call=True
    )
    def toggle_lock(should_train: bool):
        # TODO: when we lock, we should also start running the ml algos
        # since it might take longer: progress bar for each algo
        # lock all previous tabs
        # maybe add a stop button to stop all algos with no results
        global graph
        if not should_train:
            MLLockBuilder.is_locked = False
            MLLockBuilder.training_done = False
            return (
                [],
                dbc.Row(
                    children=[
                        dbc.Col(MLLockBuilder(len(graph.data_sets) == 0), width="10")
                    ],
                    justify="center"
                ),
                False
            )

        all_scores: list[tuple[pd.DataFrame, dict, MechanismType]] = []
        try:
            # TODO: should be a cancellable job via button?
            print("running all ml algos...")
            for data_set in graph.data_sets:
                row = dbc.Row(justify="center")
                row.children = []
                sources = data_set["s"]
                assert isinstance(sources, list)
                target = data_set["t"]
                assert isinstance(target, str)
                data = graph.data
                assert data is not None
                target_node = graph.get_node_by_id(target)
                assert target_node is not None
                mechanism_type = target_node.mechanism_metadata.mechanism_type
                if mechanism_type == "regression":
                    scores = Regression().evaluate_models(
                        data=data,
                        sources=sources,
                        target=target,
                    )
                else:
                    scores = Classification().evaluate_models(
                        data=data,
                        sources=sources,
                        target=target,
                    )
                    scores = pd.concat([
                        scores,
                        SemiSupervisedClassification().evaluate_models(
                            data=data,
                            sources=sources,
                            target=target,
                        )
                    ])
                    scores = pd.concat([
                        scores,
                        SelfTrainingClassification().evaluate_models(
                            data=data,
                            sources=sources,
                            target=target,
                        )
                    ]).sort_values(by=["mean"], ascending=False)
                all_scores.append((scores, {"source": sources, "target": target}, mechanism_type))

        except Exception as e:
            MLLockBuilder.is_locked = False
            MLLockBuilder.training_done = False
            return (
                [],
                dbc.Row(
                    children=[
                        dbc.Col(MLLockBuilder(True), width="10")
                    ],
                    justify="center"
                ),
                True
            )

        MLLockBuilder.is_locked = False
        MLLockBuilder.training_done = True
        return (
            MLResultViewer(all_scores).children,
            dbc.Row(
                children=[
                    dbc.Col(MLLockBuilder(), width="10")
                ],
                justify="center"
            ),
            True
        )

    @callback(
        Output("tab4", "disabled", allow_duplicate=True),
        Output("tab5", "disabled", allow_duplicate=True),
        Output("tab6", "disabled", allow_duplicate=True),
        Output("tab7", "disabled", allow_duplicate=True),
        Output("tab8", "disabled", allow_duplicate=True),
        Output("tabs", "value", allow_duplicate=True),
        Output("global-reset-button", "disabled", allow_duplicate=True),
        Input("ml-lock-store", "data"),
        prevent_initial_call=True
    )
    def toggle_ui_components(do):
        if ctx.triggered_id != "ml-lock-store":
            raise PreventUpdate()

        if do is not True:
            raise PreventUpdate()

        match (MLLockBuilder.is_locked, MLLockBuilder.training_done):
            case True, _:
                return (
                    True,
                    True,
                    True,
                    False,
                    True,
                    "tab-7",
                    True,
                )
            case False, True:
                return (
                    True,
                    False,
                    True,
                    False,
                    False,
                    "tab-7",
                    False,
                )
            case False, False:
                return (
                    False,
                    False,
                    False,
                    False,
                    True,
                    "tab-7",
                    False,
                )
            case _:
                print("this should not be possible")
                raise PreventUpdate()

    @callback(
        Output("ml-lock-store", "data"),
        Input("ml-lock-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def check_ml_train_prerequisites(clicked):
        if not clicked:
            raise PreventUpdate()

        if ctx.triggered_id != "ml-lock-button":
            raise PreventUpdate()

        global graph
        MLLockBuilder.is_locked = True
        if len(graph.data_sets) == 0:
            return True

        if MLLockBuilder.training_done is True:
            MLLockBuilder.training_done = False
            return True

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

