from enum import StrEnum
from typing import Self
from dash import html, dcc
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash_cytoscape import Cytoscape
from random import choice
import numpy as np

from models.graph import graph
from views.graph import GraphBuilder
from utils.latexify import py_to_latex


class NodeViewer(html.Div):
    def __init__(self, node_id: str):
        super().__init__(id="node-viewer")
        self.children = []
        container = dbc.Col()
        container.children = []
        node = graph.get_node_by_id(node_id)
        assert node is not None
        # TODO: 1) distribution for noise
        noise = np.array(list(node.noise.data.values())).flatten()
        noise_graph = ff.create_distplot(
            [noise], [node.name or node.id_], show_rug=False, bin_size=0.2, colors=["blue"]
        )
        container.children.append(dbc.Row(dcc.Graph("data-summary-noise-view", figure=noise_graph, config={"staticPlot": True})))

        # TODO: 2) distribution for data
        data = node.data
        assert data is not None
        if node.mechanism_metadata.mechanism_type == "regression":
            data_graph = ff.create_distplot(
                [data], [node.name or node.id_], show_rug=False, bin_size=0.2, colors=["green"]
            )
        else:
            unique, counts = np.unique(data, return_counts=True)
            data_graph = go.Figure(go.Pie(values=counts, labels=[str(x) for x in unique]))

        container.children.append(dbc.Row(dcc.Graph("data-summary-data-view", figure=data_graph, config={"staticPlot": True})))
        # TODO: 3) mechanisms
        in_nodes = [w for w in [graph.get_node_by_id(x) for x in node.in_nodes] if w is not None]
        in_nodes = [x.name or x.id_ for x in in_nodes]
        in_nodes.append(f"n_{node.name or node.id_}")
        causes = ", ".join(in_nodes)
        formulas = node.mechanism_metadata.get_formulas()
        mechanism_type = node.mechanism_metadata.mechanism_type
        mechanism_viewer = html.Div()
        mechanism_viewer.children = []
        if mechanism_type == "regression":
            try:
                x = py_to_latex(f"f({causes})", in_nodes)
                y = py_to_latex(f"{list(formulas.values())[0]}", in_nodes)
                latex_formula = x + ":=" + y
            except:
                latex_formula = py_to_latex(f"f({causes})", in_nodes) + " := \\text{<invalid>}"
            mechanism_viewer.children.append(
                dcc.Markdown(f"$${latex_formula}$$", mathjax=True)
            )
        else:
            for class_id, formula in formulas.items():
                try:
                    x = py_to_latex(f"f_{class_id}({causes})", in_nodes)
                    y = py_to_latex(f"{formula}", in_nodes)
                    latex_formula = x + ":=" + y
                except:
                    latex_formula = py_to_latex(f"f_{class_id}({causes})", in_nodes) + " := \\text{<invalid>}"
                mechanism_viewer.children.append(
                    dcc.Markdown(f"$${latex_formula}$$", mathjax=True)
            )
        container.children.append(dbc.Row(mechanism_viewer))
        self.children.append(container)


class GraphViewer(html.Div):
    def __init__(self):
        super().__init__()
        # TODO: 1) left side dropdown, reset button and graph
        # TODO: 2) right side noise distr, data distr, mechanisms (maybe make it tabbed)


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
        self.style = {
            # "width": "80%",
            # "margin-inline": "auto",
            # "border": "1px solid black"
        }
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
                dbc.Col(NodeViewer("a"))
            ]),
        ])

        scatter_plot = px.scatter_matrix(data)
        self.children.extend([
            html.H3("scatter plot"),
            dcc.Graph(id="scatter-plot", figure=scatter_plot, config={"staticPlot": True})
        ])

        for corr in ["pearson", "kendall", "spearman"]:
            mat = data.corr(method=corr)
            self.children.append(
                html.Div([
                    html.H3(f"correlation: {corr}"),
                    dcc.Graph(id=corr, figure=px.imshow(mat, text_auto=True), config={"staticPlot": True})
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
                dcc.Graph(id="scatter-graph", figure=scatter_graph, config={"staticPlot": True})
            ]),
        )

