from dash import html, dcc
import dash_bootstrap_components as dbc

class MLLockBuilder(html.Div):
    is_locked: bool = False
    def __init__(self, error: bool = False):
        super().__init__(id="ml-lock-builder")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }

        buttons = []
        if MLLockBuilder.is_locked:
            buttons.extend([
                html.Button(
                    "Unlock", 
                    id="ml-lock-button",
                    className="one-button",
                    style={
                        "margin-right": "10px"
                    }
                ),
                html.Button(
                    "Export Graph",
                    id="export-graph-ml",
                    className="one-button",
                ),
                dcc.Download(id="export-graph-text-ml"),
                dbc.Alert(
                    "Models trained and evaluated.\nExport graph or unlock to change the configuration",
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
                    "Start training",
                    id="ml-lock-button",
                    className="one-button",
                ),
                html.Button(
                    "Export Graph",
                    id="export-graph-ml",
                    className="one-button",
                    disabled=True
                ),
            ])
            if error is False:
                buttons.append(
                    dbc.Alert(
                        "Depending on the configuratin, the Training might take a while.",
                        color="info",
                        style={
                            "white-space": "pre-line",
                            "margin-top": "10px"
                        }
                    )
                )
            else:
                buttons.append(
                    dbc.Alert(
                        "No training set has been specified yet.\nCheck the ML Prep Tab!",
                        color="danger",
                        style={
                            "white-space": "pre-line",
                            "margin-top": "10px"
                        }
                    )
                )

        self.children = [
            dcc.Store(id="ml-prep-store", data=False),
            dbc.Row(
                html.H5("Train & evaluate models:")
            ),
            dbc.Row(
                dbc.Col(
                    buttons,
                    width="6"
                ),
                justify="center"
            )
        ]
