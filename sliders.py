# TODO: clean slider behavior, show min, max and actual

from dash import Dash, callback, html, Output, Input, State, ALL, MATCH
from dash.dcc import Slider, RangeSlider, Input as InputField, Dropdown
import dash_bootstrap_components as dbc
from distributions_builder import DistributionsEntry
from typing import Tuple, Optional


from distributions_builder import DISTRIBUTION_MAPPING


class DistributionSlider(html.Div):
    def __init__(self, id, distribution: Optional[Tuple[str, DistributionsEntry]] = None):
        super().__init__(id=id)
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.distribution = distribution or list(DISTRIBUTION_MAPPING.items())[0]
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
                    "index": f"{id}-{param}"
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
                    "index": f"{id}-{param}"
                }
            )
            sliders.children.append(dbc.Col(new_slider))

            # max input field
            max_field = InputField(
                id={
                    "type": "input-slider-max",
                    "index": f"{id}-{param}"
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
                        id={
                            "type": "distribution-options",
                            "index": id
                        },
                        options=list(DISTRIBUTION_MAPPING.keys()),
                        value=list(DISTRIBUTION_MAPPING.keys())[0]
                    )
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.Div(
                        id={
                            "type": "distribution-slider",
                            "index": id,
                        },
                        children=DistributionSlider(
                            id= {
                                "type": "slider-content",
                                "index": id
                            }
                        )
                    )
                )
            )
        ])


class DistributionBuilderComponent(html.Div):
    def __init__(self, id):
        super().__init__(id=id)
        # TODO: this singleton controls all distribution components; like graph
        self.distribution_builder = ...
        self.children = []
        


@callback(
    Output({"type": "slider-output", "index": ALL}, "children"),
    Input({"type": "slider-norm", "index": ALL}, "value"),
)
def update_output(input_):
    return input_

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

@callback(
    Output({"type": "distribution-slider", "index": MATCH}, "children"),
    Input({"type": "distribution-options", "index": MATCH}, "value"),
    Input({"type": "slider-content", "index": MATCH}, "id"),
    prevent_initial_call=True
)
def distribution_update(choice: str, id_: str):
    global DISTRIBUTION_MAPPING
    distribution = DISTRIBUTION_MAPPING.get(choice)
    assert distribution, "distr not found"
    ret = choice, distribution
    new_comp = DistributionSlider(id_, ret)
    return new_comp



if __name__ == "__main__":
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
                            DistributionComponent(id="var-a"),
                            DistributionComponent(id="var-b")
                        ]),
                        dbc.Col(html.Div("abc"))
                    ]
                )
            ),
        ])
    ])
    app.run(debug=True)
