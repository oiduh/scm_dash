from dash import html, dcc
import plotly.express as px

from models.graph import graph


class DataSummaryViewer(html.Div):
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
            dcc.Graph(id="scatter_plot", figure=scatter_plot)
        ]

        for corr in ["pearson", "kendall", "spearman"]:
            mat = data.corr(method=corr)
            self.children.append(
                html.Div([
                    html.H3(f"correlation: {corr}"),
                    dcc.Graph(id=corr, figure=px.imshow(mat, text_auto=True))
                ])
            )

