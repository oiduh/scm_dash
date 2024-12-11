import logging

from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from utils.logger import DashLogger
from views.data_summary import DataSummaryViewer


LOGGER = DashLogger(name="DataSummary", level=logging.DEBUG)


def setup_callbacks() -> None:
    LOGGER.info("initializing data summary callbacks")

    @callback(
        Output("data-summary-viewer", "children", allow_duplicate=True),
        Input("scatter-x", "value"),
        Input("scatter-y", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def select_nodes(first_node: str, second_node: str):
        print('select nodes')
        if DataSummaryViewer.scatter_x == first_node and DataSummaryViewer.scatter_y == second_node:
            print('not updating')
            raise PreventUpdate

        print('updating')
        DataSummaryViewer.scatter_x = first_node
        DataSummaryViewer.scatter_y = second_node
        return DataSummaryViewer().children
