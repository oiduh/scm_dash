from dash import html, dcc
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_cytoscape import Cytoscape

from models.graph import graph
from views.graph import GraphBuilder


class DataSummaryViewer(html.Div):
    scatter_x: str | None = None
    scatter_y: str | None = None
    def __init__(self):
        super().__init__(id="data-summary-viewer")
        data = graph.data
        if data is None:
            self.children = []
            return 

        # print(data.columns)
        scatter_plot = px.scatter_matrix(data)
        self.children = [
            html.H3("scatter plot"),
            dcc.Graph(id="scatter-plot", figure=scatter_plot)
        ]

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

        self.children.extend([
            dcc.Dropdown(
                # options=self.Layouts.get_all(),
                options=["circle", "nothing"],
                value="circle",
                id="layout-choices-2",
                searchable=False,
                multi=False,
                clearable=False
            ),
            # html.H3(f"Layout: {1}"),
            Cytoscape(
                id="network-graph",
                layout={"name": "circle"},
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
            )
        ])
