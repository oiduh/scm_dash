from dash import html, dcc
import dash_bootstrap_components as dbc

class LockDataBuilder(html.Div):
    is_locked: bool = False
    def __init__(self):
        super().__init__(id="data-generation-builder")
        buttons = []
        if LockDataBuilder.is_locked:
            buttons.extend([
                html.Button("Unlock", id="lock-button"),
                html.Button("Export Graph", id="export-graph"),
                dcc.Download(id="export-graph-text")
            ])
        else:
            buttons.append(
                html.Button("Lock", id="lock-button"),
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


class LockDataViewer(html.Div):
    error: bool = False
    def __init__(self):
        super().__init__(id="data-generation-viewer")
        self.children = []
        self.children.append(
            dcc.Loading(
                id="loading-1",
                type="default",
                children=html.Div(id="loading-output-1", children=["test"]),
                overlay_style={"visibility":"visible", "filter": "blur(2px)"},
            ),
        )
        if LockDataBuilder.is_locked:
            self.children.append(
                html.P("data generated")
            )
        elif LockDataViewer.error is True:
            self.children.append(
                html.P("failed to generate data. check your mechanisms")
            )
        else:
            self.children.append(
                html.P("no data generated yet")
            )


