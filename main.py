from dash import Dash, html
import dash_bootstrap_components as dbc

from views.utils import Placeholder
from views.graph import GraphBuilder, GraphViewer
from views.noise import NoiseBuilder, NoiseViewer
from views.mechanism import MechanismBuilder

from controllers import setup_callbacks


app = Dash(
    __name__, external_stylesheets=[dbc.themes.CERULEAN],
    prevent_initial_callbacks=True
)
app.layout = html.Div([
    html.Div("Causality App"),
    html.Hr(),
    html.Div([
        dbc.Tabs(id="tabs", children=[
            dbc.Tab(id="tab1", label="Graph Builder", children=dbc.Row(children=[
                dbc.Col(GraphBuilder()),
                dbc.Col(GraphViewer()),
            ])),
            dbc.Tab(id="tab2", label="Distribution Builder", children=dbc.Row(children=[
                dbc.Col(NoiseBuilder()),
                dbc.Col(NoiseViewer()),
            ])),
            dbc.Tab(id="tab3", label="Mechanism Builder", children=dbc.Row(children=[
                dbc.Col(MechanismBuilder()),
                dbc.Col(Placeholder("view3")),
            ])),
        ])
    ])
])
setup_callbacks()
app.run(debug=True,)

