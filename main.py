from dash import Dash, html
import dash_bootstrap_components as dbc

from views.utils import Placeholder
from views.graph import GraphBuilder

from controllers import setup_callbacks


app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
app.layout = html.Div([
    html.Div("Causality App"),
    html.Hr(),
    html.Div([
        dbc.Tabs(id="tabs", children=[
            dbc.Tab(id="tab1", label="Graph Builder", children=dbc.Row(children=[
                dbc.Col(GraphBuilder()),
                dbc.Col(Placeholder("view1")),
            ])),
            dbc.Tab(id="tab2", label="Distribution Builder", children=dbc.Row(children=[
                dbc.Col(Placeholder("config2")),
                dbc.Col(Placeholder("view2")),
            ])),
            dbc.Tab(id="tab3", label="Mechanism Builder", children=dbc.Row(children=[
                dbc.Col(Placeholder("config3")),
                dbc.Col(Placeholder("view3")),
            ])),
        ])
    ])
])
setup_callbacks()
app.run(debug=True,)

