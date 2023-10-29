from dash import Dash, callback, html, Output, Input, State, ALL, MATCH, ctx
from dash.dcc import Slider, Input as InputField, Dropdown, Graph
import dash_bootstrap_components as dbc
from distributions_builder import DistributionsEntry, DISTRIBUTION_MAPPING, Range
from typing import Tuple, Optional, List, Dict
from graph_builder import GraphBuilderComponent, graph_builder_component
import plotly.figure_factory as ff
import numpy as np


DISTRIBUTION_VALUES_TRACKER: Dict[str, Dict[str, float]] = {}


class DistributionSlider(html.Div):
    def __init__(self, id, distribution: Optional[Tuple[str, DistributionsEntry]] = None):
        super().__init__(id=id)
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.id = {
            "type": "slider-content",
            "index": id
        }
        self.distribution = distribution or list(DISTRIBUTION_MAPPING.items())[0]
        # distribution_type = self.distribution[0]
        distribution_values = self.distribution[1].values
        self.children = []
        for param, initial_values in distribution_values.items():
            slider_content = dbc.Col()
            slider_content.children = []
            slider_content.children.append(dbc.Row(dbc.Col(html.Label(param)), align="center"))

            sliders = dbc.Row()
            sliders.children = []

            values = DISTRIBUTION_VALUES_TRACKER.get(f"{id}-{param}")
            if values:
                min_ = values.get("min")
                max_ = values.get("max")
                value_ = values.get("value")
            else:
                min_ = initial_values.min
                max_ = initial_values.max
                value_ = initial_values.max
                
            min_field = InputField(
                id={
                    "type": "input-slider-min",
                    "index": f"{id}-{param}"
                },
                type="number", min=-100, max=100, value=min_,
                style={"width": "99%"}
            )
            sliders.children.append(dbc.Col(html.Label("min_field"), width=1))
            sliders.children.append(dbc.Col(min_field, width=1))

            # actual slider
            step = 1 if initial_values.num_type == "int" else 0.01
            new_slider = Slider(
                min=min_, max=max_, value=value_, step=step,
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
                type="number", min=-100, max=100, value=max_,
                style={"width": "99%"}
            )
            sliders.children.append(dbc.Col(html.Label("max_field"), width=1))
            sliders.children.append(dbc.Col(max_field, width=1))

            slider_content.children.append(sliders)
            self.children.append(slider_content)


class DistributionComponent(html.Div):
    def __init__(self, id, distribution: Optional[Tuple[str, DistributionsEntry]] = None):
        super().__init__(id=id)
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.id = id
        self.children = []
        self.distribution = distribution or list(DISTRIBUTION_MAPPING.items())[0]
        self.children.extend([
            dbc.Row(html.Label(f"Variable: {id}")),
            html.Hr(),
            dbc.Row([
                dbc.Col(html.Label("Distribution: "), width="auto"),
                dbc.Col(
                    Dropdown(
                        id={
                            "type": "distribution-options",
                            "index": id
                        },
                        options=list(DISTRIBUTION_MAPPING.keys()),
                        value=self.distribution[0]
                    )
                )
            ]),
            dbc.Row(
                dbc.Col(
                    html.Div(
                        id={
                            "type": "slider-div",
                            "index": id,
                        },
                        children=DistributionSlider(
                            id=id,
                            distribution=self.distribution
                        )
                    )
                )
            )
        ])


class DistributionBuilderComponent(html.Div):
    # TODO: this class needs a callback -> when nodes added/deleted/updated
    def __init__(self, id, graph_builder_comp: GraphBuilderComponent):
        super().__init__(id=id)
        # TODO: this singleton controls all distribution components; like graph
        self.children: List[DistributionComponent] = []
        self.nodes = graph_builder_comp.graph_builder.graph
        for node in self.nodes.keys():
            self.children.append(DistributionComponent(node))

    def add_node(self):
        self.children = []
        for x in self.nodes.keys():
            self.children.append(DistributionComponent(x))

    def remove_node(self, node):
        self.children = []
        for x in self.nodes.keys():
            self.children.append(DistributionComponent(x))


distribution_builder_component = DistributionBuilderComponent(
    id="distribution-builder-component",
    graph_builder_comp=graph_builder_component
)


class DistributionView(html.Div):
    def __init__(self, id):
        super().__init__(id=id)
        self.children = []
        data = np.random.normal(0, 1, size=500)
        fig = ff.create_distplot([data], group_labels=["a"], show_rug=False)
        graph = Graph(id="some_graph", figure=fig)
        self.children.append(
            graph
        )

distribution_view = DistributionView(id="distr_view")


# slider specific callbacks

@callback(
    Output({"type": "slider-norm", "index": MATCH}, "min"),
    Output({"type": "slider-norm", "index": MATCH}, "max"),
    Output({"type": "slider-norm", "index": MATCH}, "tooltip"),
    Input({"type": "input-slider-min", "index": MATCH}, "value"),
    Input({"type": "input-slider-max", "index": MATCH}, "value"),
    Input({"type": "slider-norm", "index": MATCH}, "value"),
    Input({"type": "slider-norm", "index": MATCH}, "tooltip"),
    State({"type": "slider-norm", "index": MATCH}, "id")
)
def slider_sync(input1, input2, input3, tt, id_):
    print(f"<{input1}>-<{input2}>-<{input3}>")
    print(id_)
    DISTRIBUTION_VALUES_TRACKER.update({
        id_.get("index"): {
            "min": input1,
            "max": input2,
            "value": input3,
        }
    })
    import json
    print(json.dumps(DISTRIBUTION_VALUES_TRACKER, indent=2))
    return input1, input2, tt

@callback(
    Output({"type": "slider-div", "index": MATCH}, "children"),
    Input({"type": "distribution-options", "index": MATCH}, "value"),
    Input({"type": "slider-content", "index": MATCH}, "id"),
    prevent_initial_call=True
)
def distribution_update(choice: str, id_: str):
    distribution = DISTRIBUTION_MAPPING.get(choice)
    assert distribution, "distr not found"
    ret = choice, distribution
    new_comp = DistributionSlider(id_, ret)
    return new_comp
