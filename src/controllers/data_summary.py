import logging
import json

from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from utils.logger import DashLogger
from views.data_summary import DataSummary, DataSummaryViewer, NodeViewer, StaticGraph
from views.graph import GraphBuilder


# TODO: add logs to functions
LOGGER = DashLogger(name="DataSummary", level=logging.DEBUG)


def setup_callbacks() -> None:
    LOGGER.info("initializing data summary callbacks")

    @callback(
        Output("data-summary-static-graph", "children"),
        Input("static-graph-selected-node", "value"),
    )
    def select_variabled_in_inspector(new_value: str):
        if new_value == StaticGraph.selected_node:
            raise PreventUpdate()
        StaticGraph.selected_node = new_value
        return StaticGraph().children

    @callback(
        Output("summary-graph", "layout", allow_duplicate=True),
        Input("layout-choices-summary", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def update_layout_choice(new_value: DataSummaryViewer.Layouts | None):
        if not new_value:
            raise PreventUpdate()
        DataSummaryViewer.layout = new_value
        return {"name": new_value, "animate": True}

    @callback(
        Output("data-summary-static-graph", "children", allow_duplicate=True),
        Input("summary-graph", "tapNodeData"),
        prevent_initial_call=True
    )
    def show_selected_node(data):
        if data is None:
            raise PreventUpdate()
        node_id = data.get("id")  # also 'label'
        assert node_id is not None
        StaticGraph.selected_node = node_id
        return StaticGraph().children

    # @callback(
    #     Output("data-summary-container", "children", allow_duplicate=True),
    #     Input("scatter-x", "value"),
    #     Input("scatter-y", "value"),
    #     prevent_initial_call="initial_duplicate"
    # )
    # def select_nodes(first_node: str, second_node: str):
    #     if DataSummaryViewer.scatter_x == first_node and DataSummaryViewer.scatter_y == second_node:
    #         raise PreventUpdate
    #
    #     DataSummaryViewer.scatter_x = first_node
    #     DataSummaryViewer.scatter_y = second_node
    #     return DataSummary().children

