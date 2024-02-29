from dash import MATCH, callback, Output, Input, State, ctx
from dash.exceptions import PreventUpdate

from models.graph import graph
from views.noise import NoiseNodeBuilder


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
        Input({"type": "slider-min", "index": MATCH}, "value"),
        Input({"type": "current-value", "index": MATCH}, "value"),
        Input({"type": "slider-max", "index": MATCH}, "value"),
        Input({"type": "slider", "index": MATCH}, "min"),
        Input({"type": "slider", "index": MATCH}, "value"),
        Input({"type": "slider", "index": MATCH}, "max"),
        State({"type": "current-value", "index": MATCH}, "id"),
        prevent_initial_call=True
    )
    def slider_update(
        slider_min: float | None, current_value: float | None, slider_max: float | None,
        input_min: float, input_value: float, input_max: float,
        id_: dict[str, str]
    ):
        if slider_min is None or current_value is None or slider_max is None:
            raise PreventUpdate
        print(ctx.triggered_prop_ids)
        print(ctx.triggered_id)
        print(ctx.triggered)
        var, num, param = id_.get("index", "").split("_")
        x = graph.get_node_by_id(var).data.get_distribution_by_id(num).get_parameter_by_name(param)
        x.current = min(x.max, max(x.min, max(min(current_value, slider_max), slider_min)))
        x.slider_min = max(min(x.current, slider_min), x.min)
        x.slider_max = min(max(x.current, slider_max), x.max)
        marks = {x.slider_min: str(x.slider_min), x.slider_max: str(x.slider_max)},
        tooltip = {"placement": "top", "always_visible": True},
        return x.slider_min, x.current, x.slider_max, marks[0], tooltip[0]
