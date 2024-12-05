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

