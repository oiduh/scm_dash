from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_cytoscape import Cytoscape
from views.graph import GraphBuilder
from enum import Enum


class DataGenerationBuilder(html.Div):
    is_locked: bool = False
    def __init__(self):
        super().__init__(id="data-generation-builder")
        self.children = [
            dbc.Row(
                dbc.Col(
                    html.Button(
                        "Unlock" if DataGenerationBuilder.is_locked else "Lock",
                        id="lock-button"
                    ),
                    width="auto"
                ),
                justify="center"
            )
        ]


class DataGenerationViewer(html.Div):
    """singleton graph viewer class"""
    class Layouts(str, Enum):
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
        def get_all(cls):
            return [e.value for e in cls]

    LAYOUT: str = Layouts.circle.value

    def __init__(self) -> None:
        super().__init__(id="data-generation-viewer")
        self.style = {}
        cyto_graph = Cytoscape(
            id="data-generation-graph",
            layout={
                "name": self.LAYOUT,
                "fit": True,
                "padding": 30
            },
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
        self.children = [
            dcc.Dropdown(
                options=self.Layouts.get_all(),
                value=self.LAYOUT,
                id="layout-choices-data-generation",
                searchable=False,
                multi=False,
                clearable=False
            ),
            html.H3(f"Layout: {DataGenerationViewer.LAYOUT}"),
            cyto_graph
        ]

