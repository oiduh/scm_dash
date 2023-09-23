from dash import Dash, html
import dash_bootstrap_components as dbc
from dash_cytoscape import Cytoscape
from dash.dcc import Tabs, Tab
from graph_builder import graph_builder_component, graph_builder_view


class MenuComponent(html.Div):
    def __init__(self, id):
        super().__init__(id)
        self.children = [
            html.Label("Menu"),
            html.Hr(),
            Tabs(id="menu-tab", children=[
                Tab(id="graph-builder-menu", label="Graph Builder",
                    children=graph_builder_component),
                Tab(id="distributions-menu", label="Distributions"),
                Tab(id="mechanisms-menu", label="Mechanisms"),
            ])
        ]

class GraphComponent(html.Div):
    def __init__(self, id):
        super().__init__(id)
        self.children = [
            html.Label("Graphs"),
            html.Hr(),
            Tabs(id="graph-tab", children=[
                Tab(id="graph-builder-graph", label="Graph Builder",
                    children=graph_builder_view),
                Tab(id="distributions-graph", label="Distributions"),
            ])
        ]

if __name__ == "__main__":
    app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
    app.layout = html.Div([
        html.Div("causality app"),
        html.Hr(),
        html.Div([
            dbc.Row([
                dbc.Col([
                    MenuComponent(id="menu-component")
                ]),
                dbc.Col([
                    GraphComponent(id="graph-component")
                ])
            ])
        ])
    ])
    app.run(debug=True,)
