from enum import StrEnum
from typing import Self
from dash import html, dcc
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_cytoscape import Cytoscape
from random import choice

from models.graph import graph
from views.graph import GraphBuilder


class DataSummaryViewer(html.Div):
    scatter_x: str | None = None
    scatter_y: str | None = None
    class Layouts(StrEnum):
        circle = "circle"
        random = "random"
        grid = "grid"
        concentric = "concentric"
        breadthfirst = "breadthfirst"
        # cose = "cose"
        # cose_bilkent = "cose-bilkent"
        cola = "cola"
        # euler = "euler"
        spread = "spread"
        # dagre = "dagre"
        # klay = "klay"

        @classmethod
        def get_all(cls) -> list[Self]:
            return [e for e in cls]

        @classmethod
        def get_random(cls, current: Self) -> Self:
            while (m:=choice(cls.get_all())) and m == current: pass
            return m

    layout = Layouts.circle

    def __init__(self):
        super().__init__(id="data-summary-viewer")
        data = graph.data
        if data is None:
            return
        self.children = []

        self.children.extend([
            dcc.Dropdown(
                options=self.Layouts.get_all(),
                value=self.layout,
                id="layout-choices-summary",
                searchable=False,
                multi=False,
                clearable=False
            ),
            html.Button("reset view", id="data-summary-reset", n_clicks=0),
            dbc.Row([
                dbc.Col(Cytoscape(
                    id="summary-graph",
                    layout={"name": self.layout},
                    userPanningEnabled=False,
                    zoomingEnabled=False,
                    style={"width": "100%", "height": "700px"},
                    elements=GraphBuilder.get_graph_data(),
                    stylesheet=[
                        {"selector": "node", "style": {"label": "data(label)"}},
                        {
                            "selector": "edge",
                            "style": {
                                "curve-style": "bezier",
                                "target-arrow-shape": "triangle",
                                "arrow-scale": 2,
                            },
                        },
                    ],
                )),
                dbc.Col(html.Div(id="data-summary-selected", children="nothing"))
            ]),
            
        ])

        scatter_plot = px.scatter_matrix(data)
        self.children.extend([
            html.H3("scatter plot"),
            dcc.Graph(id="scatter-plot", figure=scatter_plot)
        ])

        for corr in ["pearson", "kendall", "spearman"]:
            mat = data.corr(method=corr)
            self.children.append(
                html.Div([
                    html.H3(f"correlation: {corr}"),
                    dcc.Graph(id=corr, figure=px.imshow(mat, text_auto=True))
                ])
            )

        nodes = graph.get_nodes()
        ids = [x.id_ for x in nodes]
        if DataSummaryViewer.scatter_x is None:
            DataSummaryViewer.scatter_x = ids[0]
        if DataSummaryViewer.scatter_y is None:
            DataSummaryViewer.scatter_y = ids[1]
        scatter_graph = px.scatter(data, x=DataSummaryViewer.scatter_x, y=DataSummaryViewer.scatter_y)
        self.children.append(
            dbc.Row([
                dbc.Col(dcc.Dropdown(id="scatter-x", options=ids, value=DataSummaryViewer.scatter_x)),
                dbc.Col(dcc.Dropdown(id="scatter-y", options=ids, value=DataSummaryViewer.scatter_y)),
                dcc.Graph(id="scatter-graph", figure=scatter_graph)
            ]),
        )

