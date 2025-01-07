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

    @callback(
        Output("summary-graph", "layout", allow_duplicate=True),
        Input("layout-choices-summary", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def update_layout_choice_2(new_value: DataSummaryViewer.Layouts | None):
        print("calling update layout choices")
        if not new_value:
            raise PreventUpdate()
        DataSummaryViewer.layout = new_value
        return {"name": new_value, "animate": True}

    @callback(
        Output("summary-graph", "layout"),
        Input("data-summary-reset", "n_clicks"),
    )
    def reset_data_summary_layout(clicked):
        if not clicked:
            raise PreventUpdate()
        DataSummaryViewer.layout = DataSummaryViewer.Layouts.get_random(DataSummaryViewer.layout)
        print("resetting view: " , DataSummaryViewer.layout)
        return {"name": DataSummaryViewer.layout, "animate": True}
