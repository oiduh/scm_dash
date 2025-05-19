from dash import html, dash_table
import dash_bootstrap_components as dbc
from models.graph import graph
from models.ml import Classification, Regression, SemiSupervisedClassification, SelfTrainingClassification
import pandas as pd
from typing import Literal

class MLResultViewer(html.Div):
    def __init__(self):
        super().__init__(id="ml-result-viewer")
        self.children = []
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }

        if len(graph.data_sets) < 1:
            return

        for data_set in graph.data_sets:
            row = dbc.Row()
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
            self.children.append(MLTable(scores, {"source": sources, "target": target}, mechanism_type))
            # self.children.append(MLResultCard(scores, {"source": sources, "target": target}, mechanism_type))


class MLResultCard(html.Div):
    # TODO:separate component for table + labels
    def __init__(self, data_table: pd.DataFrame, variables: dict, mechanism_type: Literal["regression", "classification"]):
        super().__init__()
        self.children = []
        if mechanism_type == "regression":
            card = dbc.Card(
                dbc.CardBody([
                    html.H4(f"Cause: {', '.join(variables['source'])}"),
                    html.H4(f"Effect: {variables['target']}"),
                    html.H6(f"Type: {mechanism_type}"),
                    dash_table.DataTable(
                        data=data_table.to_dict("records"),
                        columns=[{"name": i, "id": i} for i in data_table.columns],
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
                    )
                ])
            )
        else:
            card = dbc.Card(
                dbc.CardBody([
                    html.H4(f"Cause: {', '.join(variables['source'])}"),
                    html.H4(f"Effect: {variables['target']}"),
                    html.H6(f"Type: {mechanism_type}"),
                    dash_table.DataTable(
                        data=data_table.to_dict("records"),
                        columns=[{"name": i, "id": i} for i in data_table.columns],
                    )
                ])
            )
        self.children.append(card)


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
        row = dbc.Row()
        row.children = []
        if mechanism_type == "regression":
            row.children.append(
                dash_table.DataTable(
                    data=data_table.to_dict("records"),
                    columns=[{"name": i, "id": i} for i in data_table.columns],
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
                )
            )
        else:
            row.children.append(
                dash_table.DataTable(
                    data=data_table.to_dict("records"),
                    columns=[{"name": i, "id": i} for i in data_table.columns],
                )
            )
        self.children.append(row)


