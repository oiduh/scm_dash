from dash import html, dash_table
import dash_bootstrap_components as dbc
from models.graph import graph
from models.mechanism import MechanismType
from models.ml import Classification, Regression, SemiSupervisedClassification, SelfTrainingClassification
import pandas as pd
from typing import Literal

class MLResultViewer(html.Div):
    def __init__(self, all_scores: list[tuple[pd.DataFrame, dict, MechanismType]] | None = None):
        super().__init__(id="ml-result-viewer")
        self.children = []
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }

        if all_scores is None:
            return

        self.children.append(html.H3("ML results:"))
        for score_tuple in all_scores:
            scores, variable_dict, mechanism_type = score_tuple
            self.children.append(MLTable(scores, variable_dict, mechanism_type))


class MLTable(html.Div):
    def __init__(self, data_table: pd.DataFrame, variables: dict, mechanism_type: Literal["regression", "classification"]):
        super().__init__()
        self.children = []
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
        self.children.extend([
            html.H5(f"Causes: {', '.join(variables['source'])}"),
            html.H5(f"Effects: {variables['target']}"),
        ])
        if mechanism_type == "regression":
            self.children.append(html.H5(f"Mechanism type: Regression"))
            self.children.append(
                dbc.Row(children=[
                    dbc.Col(),
                    dbc.Col(dash_table.DataTable(
                        data=data_table.to_dict("records"),
                        columns=[{"name": i, "id": i} for i in data_table.columns],
                        cell_selectable=False,
                        column_selectable=False,
                        row_selectable=False,
                        fill_width=False,
                        style_data_conditional=[  # type: ignore
                            {
                                "if": {
                                    "filter_query": f"{{{x}}} = {data_table[x].max()}",
                                    "column_id": f"{x}",
                                },
                                "backgroundColor": "#FF4136",
                                "color": "white",
                            } for x in ["R2", "NMSE", "NRMSE", "NMAE"]
                        ]
                    )),
                    dbc.Col()
                ])
            )
        else:
            self.children.append(html.H5(f"Mechanism type: Classification"))
            self.children.append(
                dbc.Row(children=[
                    dbc.Col(),
                    dbc.Col(dash_table.DataTable(
                        data=data_table.to_dict("records"),
                        columns=[{"name": i, "id": i} for i in data_table.columns],
                        cell_selectable=False,
                        column_selectable=False,
                        row_selectable=False,
                        fill_width=False,
                    )),
                    dbc.Col()
                ])
            )


