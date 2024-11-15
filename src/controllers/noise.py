import logging
import json

from dash import ALL, MATCH, Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from utils.logger import DashLogger
from views.noise import VariableSelection, NoiseConfig

LOGGER = DashLogger(name="NoiseController", level=logging.DEBUG)

def setup_callbacks():

    @callback(
        Output("noise-config", "children", allow_duplicate=True),
        Output("variable-selection-noise", "children", allow_duplicate=True),
        Input("noise-builder-variable", "value"),
        Input("noise-builder-sub-variable", "value"),
        prevent_initial_call=True,
    )
    def variable_selection(variable_new: str, sub_variable_new: str):
        variable_old = VariableSelection.variable
        sub_variable_old = VariableSelection.sub_variable
        if variable_new == variable_old and sub_variable_new == sub_variable_old:
            # only update if something changed
            raise PreventUpdate()

        print("called variable_selection")
        if variable_new != variable_old:
            node = graph.get_node_by_id(variable_new)
            assert node is not None
            sub_variables = node.noise.get_distribution_ids()
            VariableSelection.sub_variable = sub_variables[0]
        else:
            VariableSelection.sub_variable = sub_variable_new
        VariableSelection.variable = variable_new
        return (
            NoiseConfig().children,
            VariableSelection().children
        )

    @callback(
        Output("noise-config", "children", allow_duplicate=True),
        Input("distribution-choice", "value"),
        prevent_initial_call=True,
    )
    def change_distribution_type(new_distribution_type: str):
        print("called change_distribution_type")
        variable = VariableSelection.variable
        sub_variable = VariableSelection.sub_variable
        node = graph.get_node_by_id(variable)
        assert node is not None
        distribution = node.noise.get_distribution_by_id(sub_variable)
        assert distribution is not None
        if distribution.name == new_distribution_type:
            # only update if something changed
            raise PreventUpdate()

        distribution.change_distribution(new_distribution_type)
        return NoiseConfig().children

    @callback(
        Output("noise-config", "children", allow_duplicate=True),
        Output("variable-selection-noise", "children", allow_duplicate=True),
        Input("add-sub-variable", "n_clicks"),
        prevent_initial_call=True,
    )
    def add_sub_variable(clicked):
        if not clicked:
            raise PreventUpdate()
        print("called add_sub_variable")

        variable = VariableSelection.variable
        node = graph.get_node_by_id(variable)
        assert node is not None
        try:
            node.noise.add_distribution()
        except Exception as e:
            LOGGER.exception(
                f"Failed to add sub distribution for node with id: {variable}"
            )
            raise PreventUpdate from e

        return (
            NoiseConfig().children,
            VariableSelection().children
        )

    @callback(
        Output("noise-config", "children", allow_duplicate=True),
        Output("variable-selection-noise", "children", allow_duplicate=True),
        Input("remove-sub-variable", "n_clicks"),
        prevent_initial_call=True,
    )
    def remove_sub_variable(clicked):
        if not clicked:
            raise PreventUpdate()
        print("called remove_sub_variable")

        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None

        if len(node.noise.get_distribution_ids()) == 1:

            raise PreventUpdate("At least one must remain")
        target_distribution = node.noise.get_distribution_by_id(VariableSelection.sub_variable)
        assert target_distribution is not None

        try:
            node.noise.remove_distribution(target_distribution)
        except Exception as e:
            raise PreventUpdate from e

        # after removing a sub variable -> assign first one
        VariableSelection.sub_variable = node.noise.get_distribution_ids()[0]
        return (
            NoiseConfig().children,
            VariableSelection().children
        )

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
    def input_update(input_min, input_value, input_max, slider_value, input_id):
        print("called input_update")
        variable = VariableSelection.variable
        sub_variable = VariableSelection.sub_variable
        param = input_id.get("index")

        node = graph.get_node_by_id(variable)
        assert node is not None
        distribution = node.noise.get_distribution_by_id(sub_variable)
        assert distribution is not None

        current_ = distribution.parameters[param].current
        min_ = distribution.parameters[param].min
        max_ = distribution.parameters[param].max

        if input_value is not None and current_ != input_value:
            new_value = input_value
        elif current_ != slider_value:
            new_value = slider_value
        else:
            new_value = current_

        new_value = min(max_, max(min_, max(min(new_value, input_max), input_min)))
        new_min = max(min(new_value, input_min), min_)
        new_max = min(max(new_value, input_max), max_)

        target_parameter = distribution.get_parameter_by_name(param)
        assert target_parameter is not None
        target_parameter.min = new_min
        target_parameter.max = new_max
        target_parameter.current = new_value
        target_parameter.slider_min = new_min
        target_parameter.slider_max = new_max

        marks = (
            {
                new_min: str(new_min),
                new_max: str(new_max),
            },
        )
        tooltip = ({"placement": "top", "always_visible": True},)
        return (
            new_min,
            new_value,
            new_max,
            marks[0],
            tooltip[0],
            new_min,
            new_value,
            new_max,
        )


    # @callback(
    #     Output({"type": "slider", "index": MATCH}, "min"),
    #     Output({"type": "slider", "index": MATCH}, "value"),
    #     Output({"type": "slider", "index": MATCH}, "max"),
    #     Output({"type": "slider", "index": MATCH}, "marks"),
    #     Output({"type": "slider", "index": MATCH}, "tooltip"),
    #     Output({"type": "input-min", "index": MATCH}, "value"),
    #     Output({"type": "input-value", "index": MATCH}, "value"),
    #     Output({"type": "input-max", "index": MATCH}, "value"),
    #     Input({"type": "input-min", "index": MATCH}, "value"),
    #     Input({"type": "input-value", "index": MATCH}, "value"),
    #     Input({"type": "input-max", "index": MATCH}, "value"),
    #     Input({"type": "slider", "index": MATCH}, "value"),
    #     State({"type": "input-value", "index": MATCH}, "id"),
    #     prevent_initial_call=True,
    # )
    # def slider_update(
    #     input_min: float | None,
    #     input_value: float | None,
    #     input_max: float | None,
    #     slider_value: float,
    #     id_: dict[str, str],
    # ):
    #     triggered_context = ctx.triggered_id
    #     if triggered_context is None:
    #         raise PreventUpdate("Not a dictionary")
    #
    #     triggered_type = triggered_context.get("type", None)
    #     if triggered_type is None:
    #         raise PreventUpdate("Unknown type")
    #
    #     if input_min is None or input_value is None or input_max is None:
    #         LOGGER.error("input values not read")
    #         raise PreventUpdate
    #
    #     new_value = slider_value if triggered_type == "slider" else input_value
    #     node_id, distr_id, param_id = id_.get("index", "").split("_")
    #
    #     LOGGER.info(
    #         f"Invoked 'slider_update' for: {node_id}-{distr_id}-{param_id} via {triggered_type}"
    #     )
    #
    #     node = graph.get_node_by_id(node_id)
    #     if node is None:
    #         LOGGER.error(f"Failed to find node with id {node_id}")
    #         raise PreventUpdate("Node not found")
    #
    #     distr = node.noise.get_distribution_by_id(distr_id)
    #     if distr is None:
    #         LOGGER.error(f"Failed to find distr with id {distr_id}")
    #         raise PreventUpdate("Distr not found")
    #
    #     param = distr.get_parameter_by_name(param_id)
    #     if param is None:
    #         LOGGER.error(f"Failed to find param with id {param_id}")
    #         raise PreventUpdate("Param not found")
    #
    #     param.current = min(
    #         param.max, max(param.min, max(min(new_value, input_max), input_min))
    #     )
    #     param.slider_min = max(min(param.current, input_min), param.min)
    #     param.slider_max = min(max(param.current, input_max), param.max)
    #     marks = (
    #         {
    #             param.slider_min: str(param.slider_min),
    #             param.slider_max: str(param.slider_max),
    #         },
    #     )
    #     tooltip = ({"placement": "top", "always_visible": True},)
    #     NoiseViewer.SELECTED_NODE_ID = node_id
    #     return (
    #         param.slider_min,
    #         param.current,
    #         param.slider_max,
    #         marks[0],
    #         tooltip[0],
    #         param.slider_min,
    #         param.current,
    #         param.slider_max,
    #     )
    #
    # @callback(
    #     Output("noise-viewer", "children", allow_duplicate=True),
    #     Input({"type": "slider", "index": ALL}, "min"),
    #     Input({"type": "slider", "index": ALL}, "value"),
    #     Input({"type": "slider", "index": ALL}, "max"),
    #     Input({"type": "input-min", "index": ALL}, "value"),
    #     Input({"type": "input-value", "index": ALL}, "value"),
    #     Input({"type": "input-max", "index": ALL}, "value"),
    #     Input({"type": "slider", "index": ALL}, "id"),
    #     prevent_initial_call=True,
    # )
    # def update_graph_on_slider_release(*_):
    #     return NoiseViewer().children
    #
    # @callback(
    #     Output({"type": "noise-container", "index": MATCH}, "children"),
    #     Input({"type": "add-sub-distribution", "index": MATCH}, "n_clicks"),
    #     State({"type": "add-sub-distribution", "index": MATCH}, "id"),
    #     prevent_initial_call=True,
    # )
    # def add_sub_distribution(_, id_dict: dict[str, str]):
    #     type_ = id_dict.get("type", "")
    #     node_id = id_dict.get("index", None)
    #     if type_ != "add-sub-distribution" or node_id is None:
    #         raise PreventUpdate("wrong button")
    #
    #     LOGGER.info(f"Invoked 'add_sub_distribution' for {node_id}")
    #
    #     node = graph.get_node_by_id(node_id)
    #     if node is None:
    #         LOGGER.error(f"Failed to find node with id: {node_id}")
    #         raise PreventUpdate("Node not found")
    #
    #     try:
    #         node.noise.add_distribution()
    #     except Exception as e:
    #         LOGGER.exception(
    #             f"Failed to add sub distribution for node with id: {node_id}"
    #         )
    #         raise PreventUpdate from e
    #
    #     return NoiseContainer(node_id).children
    #
    # @callback(
    #     Output("noise-builder", "children"),
    #     Input({"type": "remove-sub-distribution", "index": ALL}, "n_clicks"),
    #     prevent_initial_call=True,
    # )
    # def remove_sub_distribution(clicked: list[int]):
    #     if not any(clicked):
    #         raise PreventUpdate
    #
    #     triggered_node: dict | None = ctx.triggered_id
    #     if triggered_node is None:
    #         raise PreventUpdate
    #
    #     index = triggered_node.get("index", None)
    #     if index is None:
    #         raise PreventUpdate
    #
    #     node_id, distr_id = index.split("_")
    #     LOGGER.info(f"Invoked 'remove_sub_distribution' for node with id: {node_id}")
    #
    #     node = graph.get_node_by_id(node_id)
    #     if node is None:
    #         LOGGER.error(f"Failed to find node with id: {node_id}")
    #         raise PreventUpdate("Node not found")
    #
    #     distr = node.noise.get_distribution_by_id(distr_id)
    #     if distr is None:
    #         LOGGER.error(f"Failed to find distr with id: {distr_id}")
    #         raise PreventUpdate("Distr not found")
    #
    #     try:
    #         node.noise.remove_distribution(distr)
    #     except Exception as e:
    #         LOGGER.exception(f"Failed to remove distribution for: {node_id}-{distr_id}")
    #         raise PreventUpdate from e
    #
    #     return NoiseBuilder().children
    #
    # @callback(
    #     Output("noise-viewer", "children")  ,
    #     Input("noise-viewer-target", "value"),
    #     prevent_initial_call=True,
    # )
    # def update_noise_viewer_choice(node_id: str):
    #     LOGGER.info("Updating noise viewer layout")
    #     if node_id not in graph.get_node_ids():
    #         raise PreventUpdate(f"Invalid node choice: {node_id}")
    #     NoiseViewer.SELECTED_NODE_ID = node_id
    #     return NoiseViewer().children
