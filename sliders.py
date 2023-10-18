# TODO: clean slider behavior, show min, max and actual

from dash import Dash, callback, html, Output, Input, State, ALL, MATCH
from dash.dcc import Slider, RangeSlider, Input as InputField, Dropdown
import dash_bootstrap_components as dbc
from distributions_builder import DistributionsEntry
from typing import Tuple


from distributions_builder import DISTRIBUTION_MAPPING


class DistributionSlider(html.Div):
    def __init__(self, id, distribution: Tuple[str, DistributionsEntry]):
        super().__init__(id=id)
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.distribution = distribution
        distribution_type = self.distribution[0]
        distribution_values = self.distribution[1].values
        self.children = []
        self.children.append(dbc.Row(dbc.Col(html.H1(distribution_type))))
        self.children.append(html.Hr())
        for param, initial_values in distribution_values.items():
            slider_content = dbc.Col()
            slider_content.children = []
            slider_content.children.append(dbc.Row(dbc.Col(html.H2(param)), align="center"))

            sliders = dbc.Row()
            sliders.children = []

            # TODO: proper id for mixture models e.g. many gaussians, same name
            # min input field
            min_field = InputField(
                id={
                    "type": "input-slider-min",
                    "index": f"{distribution_type}-{param}"
                },
                type="number", min=-100, max=100, value=initial_values.min,
                style={"width": "99%"}
            )
            sliders.children.append(dbc.Col(html.Label("min_field"), width=1))
            sliders.children.append(dbc.Col(min_field, width=1))

            # actual slider
            step = 1 if initial_values.num_type == "int" else 0.01
            new_slider = Slider(
                min=initial_values.min, max=initial_values.max,
                value=initial_values.max, step=step,
                # marks={
                #     str(range_.min): str(range_.min),
                #     str(range_.max): str(range_.max)
                # },
                marks=None,
                tooltip={"placement": "top", "always_visible": True},
                id={
                    "type": "slider-norm",
                    "index": f"{distribution_type}-{param}"
                }
            )
            sliders.children.append(dbc.Col(new_slider))

            # max input field
            max_field = InputField(
                id={
                    "type": "input-slider-max",
                    "index": f"{distribution_type}-{param}"
                },
                type="number", min=-100, max=100, value=initial_values.max,
                style={"width": "99%"}
            )
            sliders.children.append(dbc.Col(html.Label("max_field"), width=1))
            sliders.children.append(dbc.Col(max_field, width=1))

            slider_content.children.append(sliders)
            self.children.append(slider_content)


class DistributionComponent(html.Div):
    def __init__(self, id):
        super().__init__(id=id)
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.children = []
        self.children.extend([
            dbc.Row(
                dbc.Col(
                    Dropdown(
                        options=list(DISTRIBUTION_MAPPING.keys()),
                        value=list(DISTRIBUTION_MAPPING.keys())[0]
                    )
                )
            ),
            dbc.Row(
                dbc.Col(
                    DistributionSlider(id="1234", distribution=list(DISTRIBUTION_MAPPING.items())[0])
                )
            )
        ])


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
    norm_distr = DISTRIBUTION_MAPPING.get("lognorm")
    assert norm_distr is not None, "False"

    sliders = DistributionSlider(id="abc_test", distribution=("normal", norm_distr))

    app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
    app.layout = html.Div([
        html.Div("causality app"),
        html.Hr(),
        html.Div([
            html.P("sliders"),
            html.Div(
                children=dbc.Row(
                    [
                        dbc.Col([
                            DistributionComponent(id="abcd"),
                            DistributionComponent(id="efgh")
                        ]),
                        dbc.Col(html.Div("abc"))
                    ]
                )
            ),
        #     html.Div(
        #         children=[],
        #         id="slider-ouput"
        #     ),
        #     RangeSlider(
        #         0, 20,
        #         value=[5, 15],
        #         marks={"0": "0", "20": "20"},
        #         tooltip={"placement": "bottom", "always_visible": True},
        #         # TODO: initially 'mouseup' -> intervention mode with 'drag'?
        #         # updatemode="drag",
        #         id="my-range-slider"
        #     ),
        #     html.Div(
        #         children=[],
        #         id="range-slider-ouput"
        #     )
        ])
    ])
    app.run(debug=True)
