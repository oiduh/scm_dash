from dash import Dash, callback, html, Output, Input
from dash.dcc import Slider, RangeSlider
import dash_bootstrap_components as dbc

@callback(
    Output("slider-ouput", "children"),
    Input("my-slider", "value"),
)
def update_output(input_):
    return f"You have selected: {input_}"

@callback(
    Output("range-slider-ouput", "children"),
    Input("my-range-slider", "value"),
)
def update_output_range(input_):
    return f"You have selected: {input_}"

if __name__ == "__main__":
    app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
    app.layout = html.Div([
        html.Div("causality app"),
        html.Hr(),
        html.Div([
            html.P("sliders"),
            Slider(
                0, 20,
                value=10,
                marks={"0": "0", "20": "20"},
                tooltip={"placement": "bottom", "always_visible": True},
                # TODO: initially 'mouseup' -> intervention mode with 'drag'?
                # updatemode="drag",
                id="my-slider"
            ),
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
