from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_cytoscape import Cytoscape
from views.graph import GraphBuilder
from enum import Enum


class LockDataBuilder(html.Div):
    is_locked: bool = False
    def __init__(self):
        super().__init__(id="data-generation-builder")
        self.children = [
            dbc.Row(
                dbc.Col(
                    html.Button(
                        "Unlock" if LockDataBuilder.is_locked else "Lock",
                        id="lock-button"
                    ),
                    width="auto"
                ),
                justify="center"
            )
        ]


class LockDataViewer(html.Div):
    error: bool = False
    def __init__(self):
        super().__init__(id="data-generation-viewer")
        if LockDataBuilder.is_locked:
            self.children = [
                html.P("data generated")
            ]
        elif LockDataViewer.error is True:
            self.children = [
                html.P("failed to generate data. check your mechanisms")
            ]
        else:
            self.children = [
                html.P("no data generated yet")
            ]


