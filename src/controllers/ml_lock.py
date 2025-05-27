import random
import logging
from dash import callback, Output, Input, State
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
        if not should_train or MLLockBuilder.training_done:
            raise PreventUpdate()

        global graph
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
            return (
                [],
                dbc.Row(
                    children=[
                        dbc.Col(MLLockBuilder(), width="10")
                    ],
                    justify="center"
                ),
                True
            )

        MLLockBuilder.training_done = True
        return (
            MLResultViewer(all_scores).children,
            dbc.Row(
                children=[
                    dbc.Col(MLLockBuilder(), width="10")
                ],
                justify="center"
            ),
            str(uuid4())
        )

    @callback(
        Output("tab4", "disabled"),
        Output("tab5", "disabled"),
        Output("tab6", "disabled"),
        Output("tab7", "disabled"),
        Output("tab8", "disabled"),
        Output("tabs", "value"),
        Input("ml-lock-store", "data"),
        prevent_initial_call=True
    )
    def toggle_ui_components(_):
        match (MLLockBuilder.is_locked, MLLockBuilder.training_done):
            case True, False:
                return (
                    True,
                    True,
                    True,
                    False,
                    True,
                    "tab-7",
                )
            case True, True:
                return (
                    True,
                    False,
                    True,
                    False,
                    False,
                    "tab-7",
                )
            case False, False:
                return (
                    False,
                    False,
                    False,
                    False,
                    True,
                    "tab-7",
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

        global graph
        if len(graph.data_sets) == 0:
            MLLockBuilder.is_locked = False
            return False

        MLLockBuilder.is_locked = not MLLockBuilder.is_locked
        if MLLockBuilder.training_done is True:
            MLLockBuilder.training_done = False
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

