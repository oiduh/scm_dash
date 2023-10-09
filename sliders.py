# TODO: clean slider behavior, show min, max and actual

from dash import Dash, callback, html, Output, Input, State, ALL, MATCH
from dash.dcc import Slider, RangeSlider, Input as InputField
import dash_bootstrap_components as dbc


from distributions_builder import DISTRIBUTION_MAPPING

@callback(
    Output({"type": "slider-output", "index": ALL}, "children"),
    Input({"type": "slider-norm", "index": ALL}, "value"),

)
def update_output(input_):
    return input_

@callback(
    Output("range-slider-ouput", "children"),
    Input("my-range-slider", "value"),
)
def update_output_range(input_):
    return f"You have selected: {input_}"

@callback(
    Output({"type": "slider-norm", "index": MATCH}, "min"),
    Output({"type": "slider-norm", "index": MATCH}, "max"),
    Output({"type": "slider-norm", "index": MATCH}, "tooltip"),
    Input({"type": "input-slider-min", "index": MATCH}, "value"),
    Input({"type": "input-slider-max", "index": MATCH}, "value"),
    Input({"type": "slider-norm", "index": MATCH}, "tooltip")
)
def slider_sync(input1, input2, tt):
    return input1, input2, tt


if __name__ == "__main__":
    norm_distr = DISTRIBUTION_MAPPING.get("randint")
    assert norm_distr is not None, "False"
    distr_range = norm_distr.values
    sliders = []
    for kwarg, range_ in distr_range.items():
        sliders.append(dbc.Row([]))
        # sliders.append(html.H1(kwarg))
        min_field = InputField(
            id={"type": "input-slider-min", "index": f"{kwarg}"},
            type="number", min=-100, max=100, value=range_.min,
            style={"width": "99%"}
        )
        sliders[-1].children.extend([dbc.Col(html.Label("min_field"), width=1), dbc.Col(min_field, width=1)])
        step = 1 if range_.num_type == "int" else 0.01
        new_slider = Slider(
            min=range_.min, max=range_.max, value=range_.max, step=step,
            # marks={
            #     str(range_.min): str(range_.min),
            #     str(range_.max): str(range_.max)
            # },
            marks=None,
            tooltip={"placement": "bottom", "always_visible": True},
            id={"type": "slider-norm", "index": f"{kwarg}"}
        )
        sliders[-1].children.append(dbc.Col(new_slider))
        max_field = InputField(
            id={"type": "input-slider-max", "index": f"{kwarg}"},
            type="number", min=-100, max=100, value=range_.max,
            style={"width": "99%"}
        )
        sliders[-1].children.extend([dbc.Col(html.Label("max_field"), width=1), dbc.Col(max_field, width=1)])


    app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
    app.layout = html.Div([
        html.Div("causality app"),
        html.Hr(),
        html.Div([
            html.P("sliders"),
            html.Div(children=dbc.Row([dbc.Col(sliders), dbc.Col(html.Div("abc"))])),
            html.Div(
                children=[],
                id="slider-ouput"
            ),
            RangeSlider(
                0, 20,
                value=[5, 15],
                marks={"0": "0", "20": "20"},
                tooltip={"placement": "bottom", "always_visible": True},
                # TODO: initially 'mouseup' -> intervention mode with 'drag'?
                # updatemode="drag",
                id="my-range-slider"
            ),
            html.Div(
                children=[],
                id="range-slider-ouput"
            )
        ])
    ])
    app.run(debug=True,)
