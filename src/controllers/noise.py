import logging

from dash import ALL, MATCH, Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from utils.logger import DashLogger
from views.noise import NoiseBuilder, NoiseContainer, NoiseNodeBuilder, NoiseViewer

LOGGER = DashLogger(name="NoiseController", level=logging.DEBUG)


def setup_callbacks():
    @callback(
        Output({"type": "noise-node-builder", "index": MATCH}, "children"),
        Input({"type": "distribution-choice", "index": MATCH}, "value"),
        State({"type": "distribution-choice", "index": MATCH}, "id"),
        prevent_initial_call=True,
    )
    def change_distribution_choice(choice, id_: dict[str, str]):
        node_id, distr_id = id_.get("index", "").split("_")

        LOGGER.info(f"invoked 'change_distribution' for: {node_id}_{distr_id}")

        node = graph.get_node_by_id(node_id)
        if node is None:
            LOGGER.error(f"Failed to find node with id: {node_id}")
            raise PreventUpdate

        distr = node.noise.get_distribution_by_id(distr_id)
        if distr is None:
            LOGGER.error(
                f"Failed to find distr with id: {distr_id} for node with id: {node_id}"
            )
            raise PreventUpdate

        try:
            distr.change_distribution(choice)
        except Exception as e:
            LOGGER.exception(
                f"Failed to change distribution for node with id: {node_id}"
            )
            raise PreventUpdate from e

        return NoiseNodeBuilder((node_id, distr_id)).children

    @callback(
        Output({"type": "slider", "index": MATCH}, "min"),
        Output({"type": "slider", "index": MATCH}, "value"),
        Output({"type": "slider", "index": MATCH}, "max"),
        Output({"type": "slider", "index": MATCH}, "marks"),
        Output({"type": "slider", "index": MATCH}, "tooltip"),
        Output({"type": "input-min", "index": MATCH}, "value"),
        Output({"type": "input-value", "index": MATCH}, "value"),
        Output({"type": "input-max", "index": MATCH}, "value"),
        Input({"type": "input-min", "index": MATCH}, "value"),
        Input({"type": "input-value", "index": MATCH}, "value"),
        Input({"type": "input-max", "index": MATCH}, "value"),
        Input({"type": "slider", "index": MATCH}, "value"),
        State({"type": "input-value", "index": MATCH}, "id"),
        prevent_initial_call=True,
    )
    def slider_update(
        input_min: float | None,
        input_value: float | None,
        input_max: float | None,
        slider_value: float,
        id_: dict[str, str],
    ):
        triggered_context = ctx.triggered_id
        if triggered_context is None:
            raise PreventUpdate("Not a dictionary")

        triggered_type = triggered_context.get("type", None)
        if triggered_type is None:
            raise PreventUpdate("Unknown type")

        if input_min is None or input_value is None or input_max is None:
            LOGGER.error("input values not read")
            raise PreventUpdate

        new_value = slider_value if triggered_type == "slider" else input_value
        node_id, distr_id, param_id = id_.get("index", "").split("_")

        LOGGER.info(
            f"Invoked 'slider_update' for: {node_id}-{distr_id}-{param_id} via {triggered_type}"
        )

        node = graph.get_node_by_id(node_id)
        if node is None:
            LOGGER.error(f"Failed to find node with id {node_id}")
            raise PreventUpdate("Node not found")

        distr = node.noise.get_distribution_by_id(distr_id)
        if distr is None:
            LOGGER.error(f"Failed to find distr with id {distr_id}")
            raise PreventUpdate("Distr not found")

        param = distr.get_parameter_by_name(param_id)
        if param is None:
            LOGGER.error(f"Failed to find param with id {param_id}")
            raise PreventUpdate("Param not found")

        param.current = min(
            param.max, max(param.min, max(min(new_value, input_max), input_min))
        )
        param.slider_min = max(min(param.current, input_min), param.min)
        param.slider_max = min(max(param.current, input_max), param.max)
        marks = (
            {
                param.slider_min: str(param.slider_min),
                param.slider_max: str(param.slider_max),
            },
        )
        tooltip = ({"placement": "top", "always_visible": True},)
        NoiseViewer.SELECTED_NODE_ID = node_id
        return (
            param.slider_min,
            param.current,
            param.slider_max,
            marks[0],
            tooltip[0],
            param.slider_min,
            param.current,
            param.slider_max,
        )

    @callback(
        Output("noise-viewer", "children", allow_duplicate=True),
        Input({"type": "slider", "index": ALL}, "min"),
        Input({"type": "slider", "index": ALL}, "value"),
        Input({"type": "slider", "index": ALL}, "max"),
        Input({"type": "input-min", "index": ALL}, "value"),
        Input({"type": "input-value", "index": ALL}, "value"),
        Input({"type": "input-max", "index": ALL}, "value"),
        Input({"type": "slider", "index": ALL}, "id"),
        prevent_initial_call=True,
    )
    def update_graph_on_slider_release(*_):
        return NoiseViewer().children

    @callback(
        Output({"type": "noise-container", "index": MATCH}, "children"),
        Input({"type": "add-sub-distribution", "index": MATCH}, "n_clicks"),
        State({"type": "add-sub-distribution", "index": MATCH}, "id"),
        prevent_initial_call=True,
    )
    def add_sub_distribution(_, id_dict: dict[str, str]):
        type_ = id_dict.get("type", "")
        node_id = id_dict.get("index", None)
        if type_ != "add-sub-distribution" or node_id is None:
            raise PreventUpdate("wrong button")

        LOGGER.info(f"Invoked 'add_sub_distribution' for {node_id}")

        node = graph.get_node_by_id(node_id)
        if node is None:
            LOGGER.error(f"Failed to find node with id: {node_id}")
            raise PreventUpdate("Node not found")

        try:
            node.noise.add_distribution()
        except Exception as e:
            LOGGER.exception(
                f"Failed to add sub distribution for node with id: {node_id}"
            )
            raise PreventUpdate from e

        return NoiseContainer(node_id).children

    @callback(
        Output("noise-builder", "children"),
        Input({"type": "remove-sub-distribution", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def remove_sub_distribution(clicked: list[int]):
        if not any(clicked):
            raise PreventUpdate

        triggered_node: dict | None = ctx.triggered_id
        if triggered_node is None:
            raise PreventUpdate

        index = triggered_node.get("index", None)
        if index is None:
            raise PreventUpdate

        node_id, distr_id = index.split("_")
        LOGGER.info(f"Invoked 'remove_sub_distribution' for node with id: {node_id}")

        node = graph.get_node_by_id(node_id)
        if node is None:
            LOGGER.error(f"Failed to find node with id: {node_id}")
            raise PreventUpdate("Node not found")

        distr = node.noise.get_distribution_by_id(distr_id)
        if distr is None:
            LOGGER.error(f"Failed to find distr with id: {distr_id}")
            raise PreventUpdate("Distr not found")

        try:
            node.noise.remove_distribution(distr)
        except Exception as e:
            LOGGER.exception(f"Failed to remove distribution for: {node_id}-{distr_id}")
            raise PreventUpdate from e

        return NoiseBuilder().children

    @callback(
        Output("noise-viewer", "children")  ,
        Input("noise-viewer-target", "value"),
        prevent_initial_call=True,
    )
    def update_noise_viewer_choice(node_id: str):
        LOGGER.info("Updating noise viewer layout")
        if node_id not in graph.get_node_ids():
            raise PreventUpdate(f"Invalid node choice: {node_id}")
        NoiseViewer.SELECTED_NODE_ID = node_id
        return NoiseViewer().children
