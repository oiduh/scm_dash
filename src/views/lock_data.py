from dash import html, dcc
import dash_bootstrap_components as dbc

class LockDataBuilder(html.Div):
    is_locked: bool = False
    def __init__(self, error: bool=False):
        super().__init__(id="data-generation-builder")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }

        buttons = []
        if LockDataBuilder.is_locked:
            buttons.extend([
                html.Button(
                    "Unlock",
                    id="lock-button",
                    className="one-button",
                    style={
                        "margin-right": "10px"
                    }
                ),
                html.Button(
                    "Export Graph",
                    id="export-graph",
                    className="one-button",
                ),
                dcc.Download(id="export-graph-text"),
                dbc.Alert(
                    "Data generated.\nExport graph or unlock graph to change the configuration",
                    color="success",
                    style={
                        "white-space": "pre-line",
                        "margin-top": "10px"
                    }
                )
            ])
        else:
            buttons.extend([
                html.Button(
                    "Generate Data",
                    id="lock-button",
                    className="one-button",
                    style={
                        "margin-right": "10px"
                    }
                ),
                html.Button(
                    "Export Graph",
                    id="export-graph",
                    className="one-button",
                    disabled=True
                ),
            ])
            if error is False:
                buttons.append(
                    dbc.Alert(
                        "No Data generated yet",
                        color="warning",
                        style={
                            "white-space": "pre-line",
                            "margin-top": "10px"
                        }
                    )
                )
            else:
                buttons.append(
                    dbc.Alert(
                        "Failed to Generate data.\nCheck your mechanisms!",
                        color="danger",
                        style={
                            "white-space": "pre-line",
                            "margin-top": "10px"
                        }
                    )
                )

        self.children = [
            dbc.Row(
                html.H5("Generate Data:")
            ),
            dbc.Row(
                dbc.Col(
                    buttons,
                    width="6"
                ),
                justify="center"
            )
        ]
