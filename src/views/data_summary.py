from enum import StrEnum
from copy import deepcopy
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
            dbc.Row(
                dbc.Col(ScatterPlotViewerAll())
            ),
            dbc.Row(
                dbc.Col(ScatterPlotViewerInidvidual())
            ),
            dbc.Row(
                dbc.Col(CorrelationMatrixView())
            )
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
            legend = False
        else:
            unique, counts = np.unique(data, return_counts=True)
            data_graph = go.Figure(go.Pie(values=counts, labels=[str(x) for x in unique]))
            legend = True
        data_graph.update_layout(
            {
                "showlegend": legend,
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
            x = py_to_latex(f"f({causes})", in_nodes)
            y = py_to_latex(f"{list(formulas.values())[0]}", in_nodes)
            latex_formula = x + ":=" + y
            mechanism_viewer.children.append(
                dcc.Markdown(f"$${latex_formula}$$", mathjax=True)
            )
        else:
            for class_id, formula in formulas.items():
                x = py_to_latex(f"f_{class_id}({causes})", in_nodes)
                y = py_to_latex(f"{formula}", in_nodes)
                latex_formula = x + ":=" + y
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
                if kdx >= num_nodes:
                    break
                node = nodes[kdx]
                cur_col = row.children[jdx]
                cur_col.children = []

                # TODO:find a nice way to display the range of the data

                cur_col.children.append(html.H5(f"Node: {node.id_}"))
                in_nodes = "\\{\\}" if len(node.in_nodes) < 1 else "\\{" + ", ".join(node.in_nodes) + "\\}"
                cur_col.children.append(dcc.Markdown(f"$${node.id_}_{{in}} = {in_nodes}$$", mathjax=True))
                out_nodes = "\\{\\}" if len(node.out_nodes) < 1 else "\\{" + ", ".join(node.out_nodes) + "\\}"
                cur_col.children.append(dcc.Markdown(f"$${node.id_}_{{out}} = {out_nodes}$$", mathjax=True))
                noise = np.array(list(node.noise.data.values())).flatten()
                cur_col.children.append(dcc.Markdown(f"$$n_{{min}} = {noise.min():.4f}$$", mathjax=True))
                cur_col.children.append(dcc.Markdown(f"$$n_{{max}} = {noise.max():.4f}$$", mathjax=True))
                cur_col.children.append(dcc.Markdown(f"$$n_{{mean}} = {noise.mean():.4f}$$", mathjax=True))
                cur_col.children.append(dcc.Markdown(f"$$n_{{median}} = {np.median(noise):.4f}$$", mathjax=True))
                assert node.data is not None
                cur_col.children.append(dcc.Markdown(f"$$data_{{min}} = {node.data.min():.4f}$$", mathjax=True))
                cur_col.children.append(dcc.Markdown(f"$$data_{{max}} = {node.data.max():.4f}$$", mathjax=True))
                cur_col.children.append(dcc.Markdown(f"$$data_{{mean}} = {node.data.mean():.4f}$$", mathjax=True))
                cur_col.children.append(dcc.Markdown(f"$$data_{{median}} = {np.median(node.data):.4f}$$", mathjax=True))

                causes = deepcopy(node.in_nodes)
                causes.append(f"n_{node.id_}")
                causes = ", ".join(causes)
                if node.mechanism_metadata.mechanism_type == "regression":
                    cur_col.children.append(dcc.Markdown("Mechanism type: regression"))
                    x = f"f({causes})"
                    y = py_to_latex(f"{list(node.mechanism_metadata.formulas.values())[0]}", node.in_nodes)
                    formula = x + ":=" + y
                    cur_col.children.append(dcc.Markdown(f"$${formula}$$", mathjax=True))
                else:
                    cur_col.children.append(dcc.Markdown("Mechanism type: classification"))
                    for class_id, formula in node.mechanism_metadata.get_formulas().items():
                        x = f"f_{class_id}({causes})"
                        y = py_to_latex(f"{list(node.mechanism_metadata.formulas.values())[0]}", node.in_nodes)
                        formula = x + ":=" + y
                        cur_col.children.append(dcc.Markdown(f"$${formula}$$", mathjax=True))
                    else_class = f"f_{{else}}({causes})"
                    cur_col.children.append(dcc.Markdown(f"$${else_class}$$", mathjax=True))
            self.children.append(row)


class ScatterPlotViewerAll(html.Div):
    def __init__(self):
        super().__init__(id="scatter-plot-viewer-all")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
        self.children = []
        if graph.data is None:
            return
        data = graph.data
        dimensions = [
            {"label": x, "values": data[x]} for x in data.columns
        ]
        scatter_plot = go.Figure(data=go.Splom(
            dimensions=dimensions,
            # TODO: add or leave?
            # showupperhalf=False,
            # diagonal_visible=False,
        ))
        self.children.extend([
            dbc.Row(dbc.Col(html.H3("Scatter Plot - All"))),
            dbc.Row(dbc.Col(dcc.Graph(id="scatter-plot", figure=scatter_plot, config={"staticPlot": True})))
        ])


class ScatterPlotViewerInidvidual(html.Div):
    Selected_first: str | None = None
    Selected_second: str | None = None
    def __init__(self):
        super().__init__(id="scatter-plot-viewer-individual")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
        self.children = []

        if graph.data is None:
            return


        node_ids = graph.get_node_ids()
        if (
            ScatterPlotViewerInidvidual.Selected_first is None
            or ScatterPlotViewerInidvidual.Selected_second is None
        ):
            assert len(node_ids) > 1, "invalid node count"
            ScatterPlotViewerInidvidual.Selected_first = node_ids[0]
            ScatterPlotViewerInidvidual.Selected_second = node_ids[1]

        scatter_graph = px.scatter(
            graph.data,
            x=ScatterPlotViewerInidvidual.Selected_first,
            y=ScatterPlotViewerInidvidual.Selected_second
        )
        self.children.extend([
            dbc.Row(dbc.Col(html.H3("Scatter Plot - Individual"))),
            dbc.Row([
                dbc.Col(dcc.Dropdown(
                    id="scatter-plot-viewer-individual-x",
                    options=node_ids,
                    value=ScatterPlotViewerInidvidual.Selected_first,
                    style={"border-radius": "8px"},
                )),
                dbc.Col(dcc.Dropdown(
                    id="scatter-plot-viewer-individual-y",
                    options=node_ids,
                    value=ScatterPlotViewerInidvidual.Selected_second,
                    style={"border-radius": "8px"},
                )),
            ]),
            dbc.Row(
                dcc.Graph(id="scatter-graph", figure=scatter_graph, config={"staticPlot": True})
            ),
        ])


class CorrelationMatrixView(html.Div):
    def __init__(self):
        super().__init__(id="correlation-matrix-view")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
        self.children = []

        if graph.data is None:
            return

        self.children.append(dbc.Row(
            dbc.Col(html.H3("Correlation Matrices")))
        )
        row = dbc.Row()
        row.children = []
        for corr in ["pearson", "kendall", "spearman"]:
            mat = graph.data.corr(method=corr).round(4)  # type: ignore
            figure = go.Figure(px.imshow(
                mat,
                text_auto=True,
            ))
            figure.update_layout(
                title={
                    "text": corr.capitalize(),
                    "y": 0.92,
                    "x": 0.5,
                    "xanchor": "center",
                    "yanchor": "top",
                }
            )
            row.children.append(
                dbc.Col(dcc.Graph(
                    id=corr,
                    figure=figure,
                    config={"staticPlot": True},

                ))
            )
        self.children.append(row)

