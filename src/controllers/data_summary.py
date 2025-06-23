import logging
import json

from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from utils.logger import DashLogger
from views.data_summary import DataSummary, ScatterPlotViewerInidvidual, StaticGraph
from views.graph import GraphBuilder


# TODO: add logs to functions
LOGGER = DashLogger(name="DataSummary", level=logging.DEBUG)


def setup_callbacks() -> None:
    LOGGER.info("initializing data summary callbacks")

    @callback(
        Output("data-summary-static-graph", "children"),
        Input("static-graph-selected-node", "value"),
    )
    def select_variable_in_inspector(new_value: str):
        if new_value == StaticGraph.selected_node:
            raise PreventUpdate()
        StaticGraph.selected_node = new_value
        return StaticGraph().children

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

    @callback(
        Output("scatter-plot-viewer-individual", "children", allow_duplicate=True),
        Input("scatter-plot-viewer-individual-x", "value"),
        Input("scatter-plot-viewer-individual-y", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def select_nodes(first_node: str, second_node: str):
        if (
            ScatterPlotViewerInidvidual.Selected_first == first_node
            and ScatterPlotViewerInidvidual.Selected_second == second_node
        ):
            raise PreventUpdate()

        ScatterPlotViewerInidvidual.Selected_first = first_node
        ScatterPlotViewerInidvidual.Selected_second = second_node
        return ScatterPlotViewerInidvidual().children

    @callback(
        Output("data-summary-static-graph", "children", allow_duplicate=True),
        Input("layout-choices-summary", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def update_layout_choice(new_value: StaticGraph.Layouts):
        if new_value not in StaticGraph.Layouts.get_all():
            LOGGER.warn(f"not updating layout: {new_value}")
            raise PreventUpdate(f"Invalid layout choice: {new_value}")
        StaticGraph.layout = new_value
        LOGGER.info(f"Updating graph viewer layout in data summary to: {new_value}")
        return StaticGraph().children

