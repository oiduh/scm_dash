from dash import MATCH, ALL, callback, Output, Input, State, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from views.noise import NoiseBuilder, NoiseContainer, NoiseNodeBuilder, NoiseViewer


def setup_callbacks():
    @callback(
        Output({"type": "noise-node-builder", "index": MATCH}, "children"),
        Input({"type": "distribution-choice", "index": MATCH}, "value"),
        State({"type": "distribution-choice", "index": MATCH}, "id"),
        prevent_initial_call=True
    )
    def change_distribution_choice(choice, id_: dict[str, str]):
        var, num = id_.get("index", "").split("_")
        graph.get_node_by_id(var).data.get_distribution_by_id(num).change_distribution(choice)
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
        prevent_initial_call=True
    )
    def slider_update(
        input_min: float | None, input_value: float | None, input_max: float | None,
        slider_value: float, id_: dict[str, str]
    ):
        if input_min is None or input_value is None or input_max is None:
            raise PreventUpdate

        triggered_context = ctx.triggered_id
        assert isinstance(triggered_context, dict), "not a dict"
        triggered_type = triggered_context.get("type")
        print(triggered_type)
        new_value = slider_value if triggered_type == "slider" else input_value
        var, num, param = id_.get("index", "").split("_")
        x = graph.get_node_by_id(var).data.get_distribution_by_id(num).get_parameter_by_name(param)
        x.current = min(x.max, max(x.min, max(min(new_value, input_max), input_min)))
        x.slider_min = max(min(x.current, input_min), x.min)
        x.slider_max = min(max(x.current, input_max), x.max)
        marks = {x.slider_min: str(x.slider_min), x.slider_max: str(x.slider_max)},
        tooltip = {"placement": "top", "always_visible": True},
        return (
            x.slider_min, x.current, x.slider_max, marks[0], tooltip[0],
            x.slider_min, x.current, x.slider_max
        )

    @callback(
        Output({"type": "noise-container", "index": MATCH}, "children"),
        Input({"type": "add-sub-distribution", "index": MATCH}, "n_clicks"),
        State({"type": "add-sub-distribution", "index": MATCH}, "id"),
        prevent_initial_call=True
    )
    def add_sub_distribution(_, id_dict: dict[str, str]):
        type_ = id_dict.get("type")
        index_ = id_dict.get("index", "")
        if type_ != "add-sub-distribution" or not index_:
            raise PreventUpdate

        try:
            graph.get_node_by_id(index_).data.add_distribution()
        except AssertionError:
            raise PreventUpdate
        return NoiseContainer(index_).children

    @callback(
        Output("noise-builder", "children"),
        Input({"type": "remove-sub-distribution", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def remove_sub_distribution(clicked: list[int]):
        if not any(clicked):
            raise PreventUpdate

        triggered_node: dict | None = ctx.triggered_id
        if not triggered_node or not (node_id := triggered_node.get("index")):
            raise PreventUpdate

        main, sub = node_id.split("_")
        try:
            to_remove = graph.get_node_by_id(main).data.get_distribution_by_id(sub)
            graph.get_node_by_id(main).data.remove_distribution(to_remove)
        except AssertionError:
            raise PreventUpdate

        return NoiseBuilder().children
        
    @callback(
        Output("noise-viewer", "children"),
        Input({"type": "view-distribution", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def view_distribution(clicked: list[int]):
        if not any(clicked):
            raise PreventUpdate

        triggered_node: dict | None = ctx.triggered_id
        if not triggered_node or not (node_id := triggered_node.get("index")):
            raise PreventUpdate

        return NoiseViewer(node_id=node_id).children

