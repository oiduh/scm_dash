from dash import Dash, callback, html, Output, Input, State, ALL, MATCH, ctx
from dash.dcc import Slider, Input as InputField, Dropdown, Graph
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from distributions_builder import DistributionsEntry, DISTRIBUTION_MAPPING, Range
from typing import Any, Tuple, Optional, List, Dict
from graph_builder import GraphBuilderComponent, graph_builder_component
import plotly.figure_factory as ff
import numpy as np
from enum import Enum


class DistributionType(str, Enum):
    simple = "simple"
    mixture = "mixture"


# values tracker
# var_name -> kwargs
# kwargs -> min, max, value

class RangeTracker:
    def __init__(self, min: float, max: float, value: float) -> None:
        self.min = min
        self.max = max
        self.value = value


class ParameterTracker:
    def __init__(self) -> None:
        self.parameter_names: Dict[str, RangeTracker] = dict()

    def get_parameter(self, parameter: str):
        return self.parameter_names.get(parameter)

    def set_parameter(self, parameter: str, ranges: RangeTracker):
        self.parameter_names.update({
            parameter: ranges
        })

class SliderValueTracker:
    variable_names: Dict[str, ParameterTracker]

    @staticmethod
    def get_parameters(variable: str):
        return SliderValueTracker.variable_names.get(variable)

    @staticmethod
    def set_value_parameters(variable: str, parameters: ParameterTracker):
        SliderValueTracker.variable_names.update({
            variable: parameters
        })


DISTRIBUTION_VALUES_TRACKER: Dict[str, Dict[str, Dict[str, float]]] = {}
DISTRIBUTION_CHOICE_TRACKER: Dict[str, Tuple[str, DistributionsEntry]] = {}



class DistributionSlider(html.Div):
    def __init__(self, id):
        super().__init__(id=id)
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.id = {
            "type": "slider-content",
            "index": id
        }
        distribution = DISTRIBUTION_CHOICE_TRACKER.get(id) or list(DISTRIBUTION_MAPPING.items())[0]
        # distribution_type = self.distribution[0]
        distribution_values = distribution[1].values
        self.children = []
        for param, initial_values in distribution_values.items():
            slider_content = dbc.Col()
            slider_content.children = []
            slider_content.children.append(dbc.Row(dbc.Col(html.Label(param)), align="center"))

            sliders = dbc.Row()
            sliders.children = []



            # NEW: replace dicts with classes
            parmeter_values = SliderValueTracker.get_parameters(id)
            if parmeter_values and (ranges:=parmeter_values.get_parameter(param)):
                min_ = ranges.min
                max_ = ranges.max
                value_ = ranges.value
            else:
                min_ = initial_values.min
                max_ = initial_values.max
                value_ = initial_values.init
                ranges = RangeTracker(min_, max_, value_)
                new_param = ParameterTracker()
                new_param.set_parameter(param, ranges)
                SliderValueTracker.set_value_parameters(id, new_param)



                


            values = DISTRIBUTION_VALUES_TRACKER.get(id)
            if values:
                values = values.get(param)
            if values:
                assert values, "error"
                min_ = values.get("min") or initial_values.min
                max_ = values.get("max") or initial_values.max
                value_ = values.get("value") or initial_values.init
            else:
                _ = DISTRIBUTION_VALUES_TRACKER.get(id) or DISTRIBUTION_VALUES_TRACKER.update({id: {}})
                DISTRIBUTION_VALUES_TRACKER.get(id).update({
                    param: {
                        "min": initial_values.min,
                        "max": initial_values.max,
                        "value": initial_values.init,
                    }
                })
                min_ = initial_values.min
                max_ = initial_values.max
                value_ = initial_values.init
                
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
    def __init__(self, id):
        super().__init__(id=id)
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.id = id
        self.children = []
        distribution = DISTRIBUTION_CHOICE_TRACKER.get(id) or list(DISTRIBUTION_MAPPING.items())[0]
        # updated_distribution = DISTRIBUTION_CHOICE_TRACKER.get(id)
        # self.distribution = updated_distribution or list(DISTRIBUTION_MAPPING.items())[0]
        self.distribution = DISTRIBUTION_CHOICE_TRACKER.get(id) or list(DISTRIBUTION_MAPPING.items())[0]
        DISTRIBUTION_CHOICE_TRACKER.update({id: self.distribution})
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
                        children=DistributionSlider(id=id)
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
            choice = "normal"
            distr = DISTRIBUTION_MAPPING.get("normal")
            assert distr, "error"
            DISTRIBUTION_CHOICE_TRACKER.update({node: (choice, distr)})
            if not DISTRIBUTION_VALUES_TRACKER.get(node):
                DISTRIBUTION_VALUES_TRACKER.update({node: {}})
            for kwargs_, range_ in distr.values.items():
                DISTRIBUTION_VALUES_TRACKER.get(node).update({
                    kwargs_: {
                        "min": range_.min,
                        "max": range_.max,
                        "value": range_.init
                    }
                })

    def add_node(self):
        self.children = []
        for node in self.nodes.keys():
            self.children.append(DistributionComponent(node))

    def remove_node(self):
        self.children = []
        for node in self.nodes.keys():
            self.children.append(DistributionComponent(node))
        # TODO: naming
        x = list(set(DISTRIBUTION_VALUES_TRACKER.keys()).difference(
            set(self.nodes.keys())
        ))
        assert len(x) == 1, "error"
        [x] = x
        DISTRIBUTION_VALUES_TRACKER.pop(x, None)
        DISTRIBUTION_CHOICE_TRACKER.pop(x, None)


distribution_builder_component = DistributionBuilderComponent(
    id="distribution-builder-component",
    graph_builder_comp=graph_builder_component
)


class DistributionViewComponent(html.Div):
    NR_POINTS = 300
    def __init__(self, id, var):
        # TODO: seed set via input
        np.random.seed(0)
        # TODO: naming
        super().__init__()
        self.id = {"type": "distr_graph", "index": id}
        values = DISTRIBUTION_VALUES_TRACKER.get(var)
        assert values, "error"
        value_dict = dict(map(lambda y: (y[0], y[1].get("value")), values.items()))
        distribution_info = DISTRIBUTION_CHOICE_TRACKER.get(var)
        assert distribution_info, "error"
        distribution_class = distribution_info[1]
        assert distribution_class, "error"
        distribution_class = distribution_class.distribution_class
        data = distribution_class.rvs(**value_dict, size=DistributionViewComponent.NR_POINTS)
        fig = ff.create_distplot([data], [id], show_rug=False, curve_type="kde")
        self.children = Graph(id=f"graph-{id}", figure=fig)
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }


class DistributionViewContainer(html.Div):
    def __init__(self, id):
        super().__init__(id=id)
        self.children = []
        self.children.append(
            html.Button(id="update_button", children="update")
        )
        self.children.extend(
            [DistributionViewComponent(id=x, var=x)
                for x in DISTRIBUTION_CHOICE_TRACKER.keys()]
        )

    def update(self):
        self.children = []
        self.children.append(
            html.Button(id="update_button", children="update")
        )
        self.children.extend(
            [DistributionViewComponent(id=x, var=x)
                for x in DISTRIBUTION_CHOICE_TRACKER.keys()]
        )

distribution_view = DistributionViewContainer(id="distr_view")


# slider specific callbacks

@callback(
    Output({"type": "slider-norm", "index": MATCH}, "min"),
    Output({"type": "slider-norm", "index": MATCH}, "max"),
    Output({"type": "slider-norm", "index": MATCH}, "tooltip"),
    Input({"type": "input-slider-min", "index": MATCH}, "value"),
    Input({"type": "input-slider-max", "index": MATCH}, "value"),
    Input({"type": "slider-norm", "index": MATCH}, "value"),
    Input({"type": "slider-norm", "index": MATCH}, "tooltip"),
    State({"type": "slider-norm", "index": MATCH}, "id"),
    prevent_initial_call=True
)
def slider_sync(input1, input2, input3, tt, id_):
    node, kwarg = id_.get("index").split("-")
    
    if DISTRIBUTION_VALUES_TRACKER.get(node) and DISTRIBUTION_VALUES_TRACKER.get(node).get(kwarg):
        DISTRIBUTION_VALUES_TRACKER.get(node).get(kwarg).update({
                "min": input1,
                "max": input2,
                "value": input3,
        })


    return input1, input2, tt

@callback(
    Output({"type": "distr_graph", "index": ALL}, "children"),
    Input({"type": "slider-norm", "index": ALL}, "value")
)
def check(input_1):
    print(input_1)
    raise PreventUpdate

@callback(
    Output({"type": "slider-div", "index": MATCH}, "children"),
    Input({"type": "distribution-options", "index": MATCH}, "value"),
    Input({"type": "slider-content", "index": MATCH}, "id"),
    prevent_initial_call=True
)
def distribution_update(choice: str, id_: dict):
    distribution = DISTRIBUTION_MAPPING.get(choice)
    assert distribution, "distr not found"
    var_name = id_.get("index")
    assert var_name, "no varname"
    DISTRIBUTION_CHOICE_TRACKER.update({var_name: (choice, distribution)})
    DISTRIBUTION_VALUES_TRACKER.update({var_name: {}})
    for kwargs_, range_ in distribution.values.items():
        DISTRIBUTION_VALUES_TRACKER.get(var_name).update({
            kwargs_: {
                "min": range_.min,
                "max": range_.max,
                "value": range_.init
            }
        })
    new_comp = DistributionSlider(var_name)
    print(DISTRIBUTION_VALUES_TRACKER)
    print(DISTRIBUTION_CHOICE_TRACKER)
    return new_comp

@callback(
    Output("distr_view", "children", allow_duplicate=True),
    Input("update_button", "n_clicks"),
    prevent_initial_call=True
)
def udpate_view(_):
    if ctx.triggered_id == "update_button":
        distribution_view.update()
    return distribution_view.children

@callback(
    Output("distr_view", "children", allow_duplicate=True),
    Input("distribution-builder-component", "children"),
    prevent_initial_call=True
)
def udpate_view_2(_):
    return distribution_view.children

