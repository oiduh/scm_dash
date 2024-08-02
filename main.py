import dash_bootstrap_components as dbc
from dash import Dash, html

from controllers import setup_callbacks
from views.graph import GraphBuilder, GraphViewer
from views.mechanism import MechanismBuilder
from views.noise import NoiseBuilder, NoiseViewer
from views.utils import Placeholder

app = Dash(
    __name__, external_stylesheets=[dbc.themes.CERULEAN], prevent_initial_callbacks=True
)
app.layout = html.Div(
    [
        html.Div("Causality App"),
        html.Hr(),
        html.Div(
            [
                dbc.Tabs(
                    id="tabs",
                    children=[
                        dbc.Tab(
                            id="tab1",
                            label="Graph Builder",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(
                                        GraphBuilder(),
                                        style={
                                            "height": "800px",
                                            "overflow": "scroll",
                                        },
                                    ),
                                    dbc.Col(GraphViewer()),
                                ],
                            ),
                        ),
                        dbc.Tab(
                            id="tab2",
                            label="Distribution Builder",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(
                                        NoiseBuilder(),
                                        style={
                                            "height": "800px",
                                            "overflow": "scroll",
                                        },
                                    ),
                                    dbc.Col(NoiseViewer()),
                                ],
                            ),
                        ),
                        dbc.Tab(
                            id="tab3",
                            label="Mechanism Builder",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(
                                        MechanismBuilder(),
                                        style={
                                            "height": "800px",
                                            "overflow": "scroll",
                                        },
                                    ),
                                    dbc.Col(Placeholder("mechanism viewer")),
                                ],
                            ),
                        ),
                    ],
                )
            ],
        ),
    ]
)
setup_callbacks()
app.run(
    debug=True,
)
