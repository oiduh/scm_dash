from dash import html, dcc
import dash_bootstrap_components as dbc
from models.graph import graph
from models.ml import Regression

class MLLockBuilder(html.Div):
    is_locked: bool = False
    def __init__(self):
        super().__init__(id="ml-lock-builder")
        buttons = []
        if MLLockBuilder.is_locked:
            # TODO:this is temporary, make an own view for results
            if len(graph.data_sets) > 0 and graph.data is not None:
                for i in graph.data_sets:
                    sources = i["s"]
                    assert isinstance(sources, list)
                    target = i["t"]
                    assert isinstance(target, str)
                    data = graph.data
                    scores = Regression().evaluate_models(
                        data=data,
                        sources=sources,
                        target=target,
                    )
                    print(f"evaluation for: {sources=}, {target=}")
                    print(scores)

            buttons.extend([
                html.Button("Unlock", id="ml-lock-button"),
            ])
        else:
            buttons.append(
                html.Button("Lock", id="ml-lock-button"),
            )
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
