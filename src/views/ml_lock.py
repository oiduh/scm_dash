from dash import html, dcc
import dash_bootstrap_components as dbc
from models.graph import graph

class MLLockBuilder(html.Div):
    is_locked: bool = False
    def __init__(self):
        super().__init__(id="ml-lock-builder")
        buttons = []
        if MLLockBuilder.is_locked:
            buttons.extend([html.Button(
                "Unlock", 
                id="ml-lock-button",
                className="one-button",
            )])
        else:
            buttons.append(html.Button(
                "Lock",
                id="ml-lock-button",
                className="one-button",
            ))
        self.children = [
            dbc.Row(
                dbc.Col(
                    buttons,
                    width="auto"
                ),
                justify="center"
            )
        ]

class MLLockViewer(html.Div):
    def __init__(self):
        # TODO: add progress bars for each data set and each algo in training
        super().__init__(id="ml-lock-viewer")
        self.children = []
