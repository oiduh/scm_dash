from dash import ALL, Input, Output, State, callback, ctx, html
from dash.exceptions import PreventUpdate

from models.graph import graph
from utils.logger import DashLogger
from views.ml_prep import MLViewer, TrainingDataSetEditor


LOGGER = DashLogger(name="MLPrep-Controller")


def setup_callbacks() -> None:
    LOGGER.info("initializing ml prep callbacks")

    @callback(
        Output("training-data-set-editor", "children", allow_duplicate=True),
        Output("ml-viewer", "children", allow_duplicate=True),
        Input("save-training-set", "n_clicks"),
        State("selected-source-ids", "value"),
        State("selected-target-id", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def save_data_set(clicked, source_ids: list[str], target_id: str):
        if not clicked:
            raise PreventUpdate()

        if len(source_ids) < 1:
            LOGGER.warning("At least on source node needed for training")
            raise PreventUpdate()

        source_id_dict = {id_: True for id_ in source_ids}
        if graph.add_data_set(source_id_dict, target_id) is False:
            LOGGER.warning("Data set already existent")
            raise PreventUpdate()

        LOGGER.info("New data set for training added")
        return (
            TrainingDataSetEditor().children,
            MLViewer().children,
        )

    @callback(
        Output("selected-source-ids", "options", allow_duplicate=True),
        Output("selected-source-ids", "value", allow_duplicate=True),
        Input("selected-target-id", "value"),
        prevent_initial_call="initial_duplicate"
    )
    def select_new_target(new_value: str):
        if ctx.triggered_id != "selected-target-id":
            raise PreventUpdate()
        if new_value == TrainingDataSetEditor.target_id:
            raise PreventUpdate()

        TrainingDataSetEditor.target_id = new_value
        global graph
        nodes = graph.get_nodes()
        target_node = graph.get_node_by_id(new_value)
        if target_node is None:
            LOGGER.warning("No target node found")
            raise PreventUpdate()

        options: list = [{
            "label": html.Span(
                node.id_ + (" (target)" if target_node.id_ in [node.name, node.id_] else ""),
                style={"padding-left": 10}
            ),
            "value": node.id_,
            "disabled": node.id_ == target_node.id_,
        } for node in nodes]
        LOGGER.info(f"New target for ml training selected: {new_value}")
        return (
            options,
            [node.id_ for node in nodes if node.id_ != target_node.id_]
        )

    @callback(
        Output("ml-viewer", "children", allow_duplicate=True),
        Input({ "type": "remove-data-set", "index": ALL}, "n_clicks"),
        prevent_initial_call="initial_duplicate"
    )
    def remove_data_set_viewer(remove_buttons: list):
        if not any(remove_buttons):
            raise PreventUpdate()
        index = remove_buttons.index(next(x for x in remove_buttons if x))
        graph.data_sets.pop(index)
        LOGGER.info("Data set removed from training")
        return MLViewer().children
