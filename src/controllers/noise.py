from dash import ALL, MATCH, Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from views.noise import NoiseBuilder, NoiseContainer, NoiseNodeBuilder, NoiseViewer


def setup_callbacks():
    @callback(
        Output({"type": "noise-node-builder", "index": MATCH}, "children"),
        Input({"type": "distribution-choice", "index": MATCH}, "value"),
        State({"type": "distribution-choice", "index": MATCH}, "id"),
        prevent_initial_call=True,
    )
    def change_distribution_choice(choice, id_: dict[str, str]):
        var, num = id_.get("index", "").split("_")
        node = graph.get_node_by_id(var)
        if node is None:
            raise PreventUpdate

        distr = node.noise.get_distribution_by_id(num)

        if distr is None:
            raise PreventUpdate

        try:
            distr.change_distribution(choice)
        except Exception as e:
            raise PreventUpdate from e

        return NoiseNodeBuilder((var, num)).children

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
        if input_min is None or input_value is None or input_max is None:
            raise PreventUpdate

        triggered_context = ctx.triggered_id
        if triggered_context is None:
            raise PreventUpdate("Not a dictionary")

        triggered_type = triggered_context.get("type", None)
        if triggered_type is None:
            raise PreventUpdate("Unknown type")

        new_value = slider_value if triggered_type == "slider" else input_value
        var, num, param_name = id_.get("index", "").split("_")

        node = graph.get_node_by_id(var)
        if node is None:
            raise PreventUpdate("Node not found")

        distr = node.noise.get_distribution_by_id(num)
        if distr is None:
            raise PreventUpdate("Distr not found")

        param = distr.get_parameter_by_name(param_name)
        if param is None:
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
        Output({"type": "noise-container", "index": MATCH}, "children"),
        Input({"type": "add-sub-distribution", "index": MATCH}, "n_clicks"),
        State({"type": "add-sub-distribution", "index": MATCH}, "id"),
        prevent_initial_call=True,
    )
    def add_sub_distribution(_, id_dict: dict[str, str]):
        type_ = id_dict.get("type", "")
        index_ = id_dict.get("index", None)
        if type_ != "add-sub-distribution" or index_ is None:
            raise PreventUpdate("wrong button")

        node = graph.get_node_by_id(index_)
        if node is None:
            raise PreventUpdate("Node not found")

        try:
            node.noise.add_distribution()
        except Exception as e:
            raise PreventUpdate from e
        return NoiseContainer(index_).children

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

        node_id = triggered_node.get("index", None)
        if node_id is None:
            raise PreventUpdate

        main, sub = node_id.split("_")
        node = graph.get_node_by_id(main)
        if node is None:
            raise PreventUpdate("Node not found")

        distr = node.noise.get_distribution_by_id(sub)
        if distr is None:
            raise PreventUpdate("Distr not found")

        try:
            node.noise.remove_distribution(distr)
        except Exception as e:
            raise PreventUpdate from e

        return NoiseBuilder().children

    @callback(
        Output("noise-viewer", "children"),
        Input({"type": "view-distribution", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def view_distribution(clicked: list[int]):
        if not any(clicked):
            raise PreventUpdate

        triggered_node: dict | None = ctx.triggered_id
        if not triggered_node:
            raise PreventUpdate

        node_id = triggered_node.get("index", None)
        if node_id is None:
            raise PreventUpdate("Node not found")

        return NoiseViewer(node_id=node_id).children
