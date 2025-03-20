import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
import dash_cytoscape as cyto

from controllers import setup_callbacks
from views.data_summary import DataSummaryViewer
from views.graph import GraphBuilder, GraphViewer
from views.mechanism import MechanismBuilder, MechanismViewer
from views.ml_prep import MLPreparation, MLViewer
from views.ml_result import MLResultViewer
from views.noise import NoiseBuilder, NoiseViewer
from views.utils import Placeholder
from views.lock_data import LockDataBuilder, LockDataViewer
from views.ml_lock import MLLockBuilder, MLLockViewer



cyto.load_extra_layouts()


app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=True
)
app.layout = html.Div(
    [
        html.Div("Causality App"),
        html.Hr(),
        html.Div(
            [
                dcc.Tabs(
                    id="tabs",
                    children=[
                        dcc.Tab(
                            id="tab1",
                            label="Graph",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(GraphBuilder()),
                                    dbc.Col(GraphViewer()),
                                ],
                            ),
                            disabled=False,
                        ),
                        dcc.Tab(
                            id="tab2",
                            label="Distribution",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(NoiseBuilder()),
                                    dbc.Col(NoiseViewer()),
                                ],
                            ),
                            disabled=False,
                        ),
                        dcc.Tab(
                            id="tab3",
                            label="Mechanism",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(MechanismBuilder()),
                                    dbc.Col(MechanismViewer()),
                                ],
                            ),
                        ),
                        dcc.Tab(
                            id="tab4",
                            label="Data Gen",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(LockDataBuilder()),
                                    dbc.Col(LockDataViewer()),
                                ],
                            ),
                            disabled=False,
                        ),
                        dcc.Tab(
                            id="tab5",
                            label="Data View",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(DataSummaryViewer()),
                                ],
                            ),
                            disabled=True
                        ),
                        dcc.Tab(
                            id="tab6",
                            label="ML Prep",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(MLPreparation()),
                                    dbc.Col(MLViewer()),
                                ],
                            ),
                            disabled=True
                        ),
                        dcc.Tab(
                            id="tab7",
                            label="ML",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(MLLockBuilder()),
                                    dbc.Col(MLLockViewer()),
                                ],
                            ),
                            disabled=True
                        ),
                        dcc.Tab(
                            id="tab8",
                            label="ML Results",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(MLResultViewer()),
                                ],
                            ),
                            disabled=True
                        ),
                    ],
                )
            ],
        ),
    ],
    # style={"width": "99vw", "height": "99vh", "margin": "0", "padding": "0", "border-style": "solid"},
)
setup_callbacks()
app.run(
    # TODO: remove this for actual use -> ram usage
    debug=True,
)
