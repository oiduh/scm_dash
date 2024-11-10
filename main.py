import dash_bootstrap_components as dbc
from dash import Dash, html

from controllers import setup_callbacks
from views.graph import GraphBuilder, GraphViewer, GraphBuilderNew
from views.mechanism import MechanismBuilder, MechanismViewer
from views.noise import NoiseBuilder, NoiseViewer
from views.utils import Placeholder
import dash_cytoscape as cyto


cyto.load_extra_layouts()


app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.CERULEAN],
    prevent_initial_callbacks=True,
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
                                    # dbc.Col(
                                    #     GraphBuilder(),
                                    #     style={
                                    #         "height": "800px",
                                    #         "overflow": "scroll",
                                    #     },
                                    # ),
                                    dbc.Col(
                                        GraphBuilderNew()
                                    ),
                                    # dbc.Col(GraphViewer()),
                                    dbc.Col(Placeholder("graph-view-place-holder"))
                                ],
                            ),
                        ),
                        dbc.Tab(
                            id="tab2",
                            label="Distribution Builder",
                            children=dbc.Row(
                                children=[
                                    # dbc.Col(
                                    #     NoiseBuilder(),
                                    #     style={
                                    #         "height": "800px",
                                    #         "overflow": "scroll",
                                    #     },
                                    # ),
                                    dbc.Col(Placeholder("noise-build-place-holder")),
                                    # dbc.Col(NoiseViewer()),
                                    dbc.Col(Placeholder("noise-view-place-holder"))
                                ],
                            ),
                        ),
                        dbc.Tab(
                            id="tab3",
                            label="Mechanism Builder",
                            children=dbc.Row(
                                children=[
                                    # dbc.Col(
                                    #     MechanismBuilder(),
                                    #     style={
                                    #         "height": "800px",
                                    #         "overflow": "scroll",
                                    #     },
                                    # ),
                                    dbc.Col(Placeholder("mechanism-view-place-holder")),
                                    # dbc.Col(MechanismViewer()),
                                    dbc.Col(Placeholder("mechanism-build-place-holder")),
                                ],
                            ),
                        ),
                    ],
                )
            ],
        ),
    ],
    style={"width": "99vw", "height": "99vh", "margin": "0", "padding": "0", "border-style": "solid"},
)
setup_callbacks()
app.run(
    # TODO: remove this for actual use -> ram usage
    debug=True,
)
