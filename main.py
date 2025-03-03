import dash_bootstrap_components as dbc
from dash import Dash, html
import dash_cytoscape as cyto

from controllers import setup_callbacks
from views.data_summary import DataSummaryViewer
from views.graph import GraphBuilder, GraphViewer
from views.mechanism import MechanismBuilder, MechanismViewer
from views.ml_prep import MLPreparation, MLViewer
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
                dbc.Tabs(
                    id="tabs",
                    children=[
                        dbc.Tab(
                            id="tab1",
                            label="Graph Builder",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(GraphBuilder()),
                                    dbc.Col(GraphViewer()),
                                ],
                            ),
                            disabled=False,
                        ),
                        dbc.Tab(
                            id="tab2",
                            label="Distribution Builder",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(NoiseBuilder()),
                                    dbc.Col(NoiseViewer()),
                                ],
                            ),
                            disabled=False,
                        ),
                        dbc.Tab(
                            id="tab3",
                            label="Mechanism Builder",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(MechanismBuilder()),
                                    dbc.Col(MechanismViewer()),
                                ],
                            ),
                        ),
                        dbc.Tab(
                            id="tab4",
                            label="lock in",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(LockDataBuilder()),
                                    dbc.Col(LockDataViewer()),
                                ],
                            ),
                            disabled=False,
                        ),
                        dbc.Tab(
                            id="tab5",
                            label="Summary",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(DataSummaryViewer()),
                                ],
                            ),
                            disabled=True
                        ),
                        dbc.Tab(
                            id="tab6",
                            label="Variable Selection",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(MLPreparation()),
                                    dbc.Col(MLViewer()),
                                ],
                            ),
                            disabled=True
                        ),
                        dbc.Tab(
                            id="tab7",
                            label="ML Lock",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(MLLockBuilder()),
                                    dbc.Col(MLLockViewer()),
                                ],
                            ),
                            disabled=True
                        ),
                        dbc.Tab(
                            id="tab8",
                            label="ML Results",
                            children=dbc.Row(
                                children=[
                                    dbc.Col(Placeholder("ml-results")),
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
