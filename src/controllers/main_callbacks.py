from models.graph import reset_graph_to_base
from dash import Input, Output, callback, ctx
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from views.graph import (
    GraphBuilder,
    GraphUploader,
    GraphViewer,
    VariableSelection as GraphVariableSelection,
)
from views.lock_data import LockDataBuilder
from views.noise import (
    NoiseBuilder,
    NoiseViewer,
)
from views.mechanism import (
    MechanismBuilder,
    MechanismConfig,
    MechanismViewer,
    VariableSelection as MechanismVariableSelection,
)


def setup_callbacks() -> None:
    @callback(
        Output("loading-4", "children"),
        Output("tab3", "children"),
        Output("tab2", "children"),
        Output("tab1", "children"),
        Output("tabs", "value"),
        Output("tab1", "disabled"),
        Output("tab2", "disabled"),
        Output("tab3", "disabled"),
        Output("tab4", "disabled"),
        Output("tab5", "disabled"),
        Output("tab6", "disabled"),
        Output("tab7", "disabled"),
        Output("tab8", "disabled"),
        Input("global-reset-button", "n_clicks"),
    )
    def reset_graph(clicked):
        if not clicked:
            raise PreventUpdate()

        if ctx.triggered_id != "global-reset-button":
            raise PreventUpdate()

        global graph
        graph = reset_graph_to_base()

        # graph view resets
        GraphUploader.last_uploaded_graph = None
        GraphVariableSelection.selected_node_id = None
        GraphViewer.LAYOUT = GraphViewer.Layouts.circle

        # noise view resets
        NoiseViewer.selected_view_option = "combined"

        # mechanism view resets
        MechanismVariableSelection.variable = None
        MechanismConfig.mechanism_type = None
        MechanismConfig.is_open = False

        # lock data view resets
        LockDataBuilder.is_locked = False
        LockDataBuilder.data_generated = False


        print('global-reset-button')

        return (
            dbc.Row(children=[
                dbc.Col(LockDataBuilder(), width="10")
            ], justify="center"),
            dbc.Row(children=[
                dbc.Col(MechanismBuilder()),
                dbc.Col(MechanismViewer()),
            ]),
            dbc.Row(children=[
                dbc.Col(NoiseBuilder()),
                dbc.Col(NoiseViewer()),
            ]),
            dbc.Row(children=[
                dbc.Col(GraphBuilder()),
                dbc.Col(GraphViewer()),
            ]),
            "tab1",
            False,
            False,
            False,
            False,
            True,
            True,
            True,
            True,
        )
