import logging

from dash import ALL, MATCH, Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from utils.logger import DashLogger
from views.noise import VariableSelection, NoiseConfig, NoiseViewer

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

        if variable_new != variable_old:
            node = graph.get_node_by_id(variable_new)
            assert node is not None
            sub_variables = node.noise.get_distribution_ids()
            VariableSelection.sub_variable = sub_variables[0]
        else:
            VariableSelection.sub_variable = sub_variable_new
        VariableSelection.variable = variable_new

        LOGGER.info(f"Selected node with id: {VariableSelection.variable}_{VariableSelection.sub_variable}")
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
        LOGGER.info(
            "Changed distribution for node with"
            f"id={VariableSelection.variable}_{VariableSelection.sub_variable} to type={new_distribution_type}"
        )
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

        variable = VariableSelection.variable
        node = graph.get_node_by_id(variable)
        assert node is not None
        try:
            new_sub_variable = node.noise.add_distribution()
        except Exception as e:
            LOGGER.exception(
                f"Failed to add sub distribution for node with id: {variable}"
            )
            raise PreventUpdate from e

        LOGGER.info(f"Added new sub variable with id={VariableSelection.variable}_{new_sub_variable}")
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
        LOGGER.info(f"Removed sub variable with id={VariableSelection.variable}_{VariableSelection.sub_variable}")
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
        # target_parameter.min = new_min
        # target_parameter.max = new_max
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
        LOGGER.info(
            f"Updated values for node with id={VariableSelection.variable}_{VariableSelection.sub_variable}: {target_parameter.__dict__}"
        )
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
    def update_graph(*_):
        return NoiseViewer().children
