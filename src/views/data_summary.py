from enum import StrEnum
from typing import Self
from dash import html, dcc
from pandas.io.formats.printing import justify
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


class DataSummary(html.Div):
    """
    container for all individual data summary components
    -> make all collapsable?
    1) graph -> static, but can change layout
       graph/node inspector -> click or select node via dropdown
       show noise and data distribution as graphs
       -> classification distribution vs. regression distr graph e.g. pie
       more visual
    2) all data stats
       -> raw stats, no graphs
       -> nodes, in nodes, out nodes, noise range, data range, mechanism type, formulas
       more textual
    3) correlation graphs
       -> all at once
       -> individual with bigger scale
    4) correlation heat maps, 3 types
    5) maybe more if useful
    """
    def __init__(self):
        super().__init__(id="data-summary-container")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
        self.children = []
        self.children.extend([
            dbc.Row(
                dbc.Col(StaticGraph())
            ),
            dbc.Row(
                dbc.Col(RawStatsViewer())
            ),
        ])


class StaticGraph(html.Div):
    class Layouts(StrEnum):
        circle = "circle"
        random = "random"
        grid = "grid"
        concentric = "concentric"
        breadthfirst = "breadthfirst"
        cola = "cola"
        spread = "spread"

        @classmethod
        def get_all(cls) -> list[Self]:
            return [e for e in cls]

        @classmethod
        def get_random(cls, current: Self) -> Self:
            while (m:=choice(cls.get_all())) and m == current: pass
            return m

    layout = Layouts.circle
    selected_node: str | None = None
    def __init__(self):
        super().__init__(id="data-summary-static-graph")
        if StaticGraph.selected_node is None:
            StaticGraph.selected_node = graph.get_node_ids()[0]

        node = graph.get_node_by_id(StaticGraph.selected_node)
        assert node is not None
        if node.data is None:
            return

        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
        self.children = []
        self.children.append(html.Div(
            children=[
                html.H5("Graph inspector:"),
                dbc.Row(
                    children=[
                        dbc.Col(html.P("Select Variable:"), width="auto"),
                        dbc.Col(
                            dcc.Dropdown(
                                options=graph.get_node_ids(),
                                value=StaticGraph.selected_node,
                                id="static-graph-selected-node",
                                searchable=False,
                                multi=False,
                                clearable=False,
                                style={"border-radius": "8px"},
                            ),
                        )
                    ]
                )
            ],
            style={
                "margin": "10px",
            }
        ))

        viewer = dbc.Row(justify="evenly")
        viewer.children = []
        viewer.children.append(dbc.Col(
            children=[
                dbc.Row(
                    children=[
                        dbc.Col(html.P("Select Layout:"), width="auto"),
                        dbc.Col(dcc.Dropdown(
                            options=self.Layouts.get_all(),
                            value=self.layout,
                            id="layout-choices-summary",
                            searchable=False,
                            multi=False,
                            clearable=False,
                            style={"border-radius": "8px"},
                        ))
                    ]
                ),
                dbc.Row(Cytoscape(
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
                ), align="center")
            ],
            style={
                "border": "solid black 2px",
                "border-radius": "8px",
                "padding": "20px",
                "margin": "10px",
                "margin-left": "20px",
            }
        ))

        node_inspector = html.Div()
        node_inspector.children = []
        # TODO:add graphs for noise distribution, data distribution and mechanism
        noise = np.array(list(node.noise.data.values())).flatten()
        noise_graph = ff.create_distplot(
            [noise], [node.name or node.id_], show_rug=False, bin_size=0.2, colors=["blue"]
        )
        noise_graph.update_layout(
            {
                "showlegend": False,
                "height": 300,
                "width": 700,
                "margin_l": 0,
                "margin_r": 0,
                "margin_t": 0,
                "margin_b": 30,
            }
        )
        node_inspector.children.extend([
            dbc.Row(html.H6("Noise distribution:")),
            dbc.Row(dcc.Graph(
                "data-summary-noise-view",
                figure=noise_graph,
                config={"staticPlot": True},
            ))
        ])

        data = node.data
        assert data is not None
        if node.mechanism_metadata.mechanism_type == "regression":
            data_graph = ff.create_distplot(
                [data], [node.name or node.id_], show_rug=False, bin_size=0.2, colors=["green"]
            )
        else:
            unique, counts = np.unique(data, return_counts=True)
            data_graph = go.Figure(go.Pie(values=counts, labels=[str(x) for x in unique]))
        data_graph.update_layout(
            {
                "showlegend": False,
                "height": 300,
                "width": 700,
                "margin_l": 0,
                "margin_r": 0,
                "margin_t": 0,
                "margin_b": 30,
            }
        )

        node_inspector.children.extend([
            dbc.Row(html.H6("Data distribution:")),
            dcc.Graph(
                "data-summary-data-view",
                figure=data_graph,
                config={"staticPlot": True},
            )
        ])

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
            # TODO: label the else class correctly
            latex_formula = py_to_latex(f"f_{'else'}({causes})", in_nodes)
            mechanism_viewer.children.append(
                dcc.Markdown(f"$${latex_formula}$$", mathjax=True)
            )
        node_inspector.children.extend([
            dbc.Row(html.H6("Mechanisms:")),
            dbc.Row(mechanism_viewer)
        ])
        viewer.children.append(dbc.Col(node_inspector, style={
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "20px",
            "margin": "10px",
            "margin-right": "20px",
        }))
        self.children.append(viewer)


class RawStatsViewer(html.Div):
    def __init__(self):
        super().__init__(id="data-summary-configuration")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
        self.children = []
        global graph
        if any(node.data is None for node in graph.get_nodes()):
            return

        self.children.append(html.H5("Raw Stats:", style={"margin": "10px"}))

        nodes = graph.get_nodes()
        num_nodes = len(nodes)
        rem = num_nodes % 3
        num_empty = 0 if rem == 0 else 3 - rem

        for idx in range(0, num_nodes + num_empty, 3):
            row = dbc.Row(
                children=[
                    dbc.Col(style={
                        "border": "solid black 2px",
                        "border-radius": "8px",
                        "padding": "10px",
                        "margin": "10px",
                        "margin-left": "22px",
                    }),
                    dbc.Col(style={
                        "border": "solid black 2px" if idx + 1 < num_nodes else None,
                        "border-radius": "8px" if idx + 1 < num_nodes else None,
                        "padding": "10px",
                        "margin": "10px",
                    }),
                    dbc.Col(style={
                        "border": "solid black 2px" if idx + 2 < num_nodes else None,
                        "border-radius": "8px" if idx + 2 < num_nodes else None,
                        "padding": "10px",
                        "margin": "10px",
                        "margin-right": "22px",
                    }),
                ],
            )
            assert row.children is not None
            for jdx in range(3):
                kdx = idx + jdx
                print(f"{idx=}, {kdx=}")
                if kdx >= num_nodes:
                    break
                node = nodes[kdx]
                cur_col = row.children[jdx]
                cur_col.children = []
                cur_col.children.append(html.H5(f"Node: {node.id_}"))
                in_nodes = "\\{\\}" if len(node.in_nodes) > 0 else "\\{" + ", ".join(node.in_nodes) + "\\}"
                cur_col.children.append(dcc.Markdown(f"$${node.id_}_{{in}} = {in_nodes}$$", mathjax=True))
                out_nodes = "\\{\\}" if len(node.out_nodes) < 1 else "\\{" + ", ".join(node.out_nodes) + "\\}"
                cur_col.children.append(dcc.Markdown(f"$${node.id_}_{{out}} = {out_nodes}$$", mathjax=True))
                noise = np.array(list(node.noise.data.values())).flatten()
                cur_col.children.append(dcc.Markdown(f"$$n_{{{node.id_}}} := \\{{ x | x \\in [{noise.min():.4f}, {noise.max():.4f}] \\}}$$", mathjax=True))
                assert node.data is not None
                cur_col.children.append(dcc.Markdown(f"$$data_{{{node.id_}}} := \\{{ x | x \\in [{node.data.min():.4f}, {node.data.max():.4f}] \\}}$$", mathjax=True))
                if node.mechanism_metadata.mechanism_type == "regression":
                    cur_col.children.append(dcc.Markdown("Mechanism type: regression"))
                    # todo: fix the formulas, as in views/mechanism.py
                    x = py_to_latex(f"f({causes})", in_nodes)
                    y = py_to_latex(f"{list(formulas.values())[0]}", in_nodes)
                    latex_formula = x + ":=" + y
                    cur_col.children.append(dcc.Markdown(f"{node.mechanism_metadata.formulas['0']}"))
                else:
                    cur_col.children.append(dcc.Markdown("Mechanism type: classification"))
                    for formula in node.mechanism_metadata.get_formulas().values():
                        cur_col.children.append(dcc.Markdown(f"{formula}"))
            self.children.append(row)
            # dcc.Markdown(f"$$f({', '.join(displayed_names)}):=$$", mathjax=True),
            # width="auto", style={"paddingTop": "10px"}


class NodeViewer(html.Div):
    def __init__(self, node_id: str):
        super().__init__(id="node-viewer")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
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
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
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
                clearable=False,
                style={"border-radius": "8px"},
            ),
            html.Button(
                "reset view",
                id="data-summary-reset",
                n_clicks=0,
                className="one-button",
            ),
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
                dbc.Col(dcc.Dropdown(
                    id="scatter-x",
                    options=ids,
                    value=DataSummaryViewer.scatter_x,
                    style={"border-radius": "8px"},
                )),
                dbc.Col(dcc.Dropdown(
                    id="scatter-y",
                    options=ids,
                    value=DataSummaryViewer.scatter_y,
                    style={"border-radius": "8px"},
                )),
                dcc.Graph(id="scatter-graph", figure=scatter_graph, config={"staticPlot": True})
            ]),
        )

