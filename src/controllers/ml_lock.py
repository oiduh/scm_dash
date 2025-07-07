import random
from dash import callback, Output, Input, ctx
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd

from models.graph import graph
from models.mechanism import MechanismType
from models.ml import Classification, Regression, SelfTrainingClassification, SemiSupervisedClassification
from utils.logger import DashLogger
from views.ml_lock import MLLockBuilder
from views.ml_result import MLResultViewer


LOGGER = DashLogger(name="MLLock-Controller")


def setup_callbacks():
    @callback(
        Output("ml-result-viewer", "children", allow_duplicate=True),
        Output("loading-7", "children", allow_duplicate=True),
        Output("ml-lock-store", "data", allow_duplicate=True),
        Input("ml-lock-store", "data"),
        prevent_initial_call=True
    )
    def toggle_lock(should_train: bool):
        global graph
        if not should_train or MLLockBuilder.is_locked is False:
            MLLockBuilder.is_locked = False
            MLLockBuilder.training_done = False
            LOGGER.info("No training required")
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
        except Exception:
            MLLockBuilder.is_locked = False
            MLLockBuilder.training_done = False
            LOGGER.exception("ML training failed")
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
        LOGGER.info("ML training completed")
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
            LOGGER.info("Not ready for ML training")
            raise PreventUpdate()

        match (MLLockBuilder.is_locked, MLLockBuilder.training_done):
            case True, _:
                LOGGER.info("Locked functions while training")
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
                LOGGER.info("Training complete, unlocking next tabs")
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
                LOGGER.info("Training failed or undone, unlocking previous tabs")
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
                LOGGER.info("This should not be possible")
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
            MLLockBuilder.training_done = False
            LOGGER.warning("Cannot perform training without data sets")
            return True

        if MLLockBuilder.training_done is True:
            MLLockBuilder.is_locked = False
            MLLockBuilder.training_done = False
            LOGGER.warning("Undoing a previously successful training")
            return True

        MLLockBuilder.is_locked = True
        LOGGER.info("Triggered training")
        return True

    @callback(
        Output("export-graph-text-ml", "data"),
        Input("export-graph-ml", "n_clicks"),
        prevent_initial_call=True
    )
    def export_data(clicked):
        if not clicked:
            raise PreventUpdate()
        LOGGER.info("Exported data set")
        return {
            "content": graph.to_dict(),
            "filename": f"graph_{random.randint(1000,9999)}.txt"
        }

