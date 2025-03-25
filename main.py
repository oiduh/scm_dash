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
    suppress_callback_exceptions=True,
    eager_loading=True,
)
app.layout = html.Div(
    [
        html.Div("Causality App"),
        html.Hr(),
        html.Div(
            [
                dcc.Tabs(
                    id="tabs",
                    value="tab-1",
                    children=[
                        dcc.Tab(
                            id="tab1",
                            label="Graph",
                            value="tab-1",
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
                            value="tab-2",
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
                            value="tab-3",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(MechanismBuilder()),
                                    dbc.Col(MechanismViewer()),
                                ],
                            ),
                            disabled=False,
                        ),
                        dcc.Tab(
                            id="tab4",
                            label="Data Gen",
                            value="tab-4",
                            children=dcc.Loading(
                                id="loading-4",
                                type="dot",
                                children=dbc.Row(
                                    children=[
                                        dbc.Col(LockDataBuilder()),
                                        dbc.Col(LockDataViewer()),
                                    ],
                                ),
                                overlay_style={"visibility":"visible", "filter": "blur(2px)"}
                            ),
                            disabled=False,
                        ),
                        dcc.Tab(
                            id="tab5",
                            label="Data View",
                            value="tab-5",
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
                            value="tab-6",
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
                            value="tab-7",
                            children=dcc.Loading(
                                id="loading-7",
                                type="dot",
                                children=dbc.Row(
                                    children=[
                                        dbc.Col(MLLockBuilder()),
                                        dbc.Col(MLLockViewer()),
                                    ],
                                ),
                                overlay_style={"visibility":"visible", "filter": "blur(2px)"}
                            ),
                            disabled=True
                        ),
                        dcc.Tab(
                            id="tab8",
                            label="ML Results",
                            value="tab-8",
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
)
setup_callbacks()
app.run(
    # TODO: remove this for actual use -> ram usage
    debug=True,
)
