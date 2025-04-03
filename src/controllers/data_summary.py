import logging
import json

from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from utils.logger import DashLogger
from views.data_summary import DataSummary, DataSummaryViewer, NodeViewer
from views.graph import GraphBuilder


# TODO: add logs to functions
LOGGER = DashLogger(name="DataSummary", level=logging.DEBUG)


def setup_callbacks() -> None:
    LOGGER.info("initializing data summary callbacks")

    @callback(
        Output("data-summary-container", "children", allow_duplicate=True),
        Input("scatter-x", "value"),
        Input("scatter-y", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def select_nodes(first_node: str, second_node: str):
        if DataSummaryViewer.scatter_x == first_node and DataSummaryViewer.scatter_y == second_node:
            raise PreventUpdate

        DataSummaryViewer.scatter_x = first_node
        DataSummaryViewer.scatter_y = second_node
        return DataSummary().children

    @callback(
        Output("summary-graph", "layout", allow_duplicate=True),
        Input("layout-choices-summary", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def update_layout_choice_2(new_value: DataSummaryViewer.Layouts | None):
        if not new_value:
            raise PreventUpdate()
        DataSummaryViewer.layout = new_value
        return {"name": new_value, "animate": True}

    @callback(
        Output("summary-graph", "elements"),
        Input("data-summary-reset", "n_clicks"),
    )
    def reset_data_summary_layout(clicked):
        if not clicked:
            raise PreventUpdate()
        return GraphBuilder.get_graph_data()

    @callback(
        Output("node-viewer", "children", allow_duplicate=True),
        Input("summary-graph", "tapNodeData"),
        prevent_initial_call=True
    )
    def show_selected_node(data):
        node = data.get("id")  # also 'label'
        assert node is not None
        return NodeViewer(node).children

    @callback(
        Output("data-summary-selected", "children", allow_duplicate=True),
        Input("summary-graph", "tapEdgeData"),
        prevent_initial_call=True
    )
    def show_selected_edge(data):
        source = data["source"]
        target = data["target"]
        return f"selected edge from '{source}' to '{target}'"
