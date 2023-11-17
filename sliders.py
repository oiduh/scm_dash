from dash import Dash, callback, html, Output, Input, State, ALL, MATCH, ctx
from dash.dcc import Slider, Input as InputField, Dropdown, Graph
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from distributions_builder import(
    DistributionsEntry, DISTRIBUTION_MAPPING, Range, Generator,
    DEFAULT_DISTRIBUTION
)
from typing import Any, Tuple, Optional, List, Dict, get_args
from graph_builder import GraphBuilderComponent, graph_builder_component
import plotly.figure_factory as ff
import numpy as np


class RangeTracker:
    def __init__(self, min: float, max: float, value: float) -> None:
        self.min = min
        self.max = max
        self.value = value


class ParameterTracker:
    def __init__(self, distribution_type: str) -> None:
        self.distribution_type = distribution_type
        distribution = DISTRIBUTION_MAPPING.get(distribution_type)
        assert distribution, "error"
        self.generator: Generator = distribution.generator
        self.parameter_names: Dict[str, RangeTracker] = dict()
        for param_, range_ in distribution.values.items():
            default_range = RangeTracker(range_.min, range_.max, range_.init)
            self.parameter_names.update({param_: default_range})

    def get_distribution_type(self):
        return self.distribution_type

    def get_ranges(self):
        return self.parameter_names

    def get_range(self, parameter: str):
        return self.parameter_names.get(parameter)

    def set_range(self, parameter: str, ranges: RangeTracker):
        self.parameter_names.update({
            parameter: ranges
        })


class SubVariableTracker:
    def __init__(self) -> None:
        self.sub_variables: Dict[str, ParameterTracker] = {}

    def get_sub_variables(self):
        return self.sub_variables

    def get_parameters(self, param: str):
        return self.sub_variables.get(param)

    def set_distribution(self, var_name: str, params: ParameterTracker):
        self.sub_variables.update({var_name: params})


class SliderTracker:
    variables: Dict[str, SubVariableTracker] = {}

    @staticmethod
    def get_variables():
        return SliderTracker.variables

    @staticmethod
    def get_sub_variables(variable: str):
        return SliderTracker.variables.get(variable)

    @staticmethod
    def add_new_variable(variable: str):
        new_distr = SubVariableTracker()
        new_params = ParameterTracker(DEFAULT_DISTRIBUTION[0])
        for param, ranges in DEFAULT_DISTRIBUTION[1].values.items():
            new_range = RangeTracker(ranges.min, ranges.max, ranges.init)
            new_params.set_range(param, new_range)
        new_distr.set_distribution(f"{variable}_1", new_params)
        SliderTracker.variables.update({variable: new_distr})

    @staticmethod
    def remove_variable(variable: str):
        assert SliderTracker.variables.get(variable) is not None, "error"
        SliderTracker.variables.pop(variable)

    @staticmethod
    def show():
        for x, y in SliderTracker.variables.items():
            print(f"{x}:")
            for a, b in y.get_sub_variables().items():
                print(f"  {a} ({b.distribution_type}):")
                for c, d in b.parameter_names.items():
                    print(f"    {c}")
                    print(f"      {d.min}")
                    print(f"      {d.max}")
                    print(f"      {d.value}")


class DistributionSlider(html.Div):

    def __init__(self, sub_variable: str, variable: str):
        super().__init__()
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.variable_name = variable
        self.id = {
            "type": "distribution-slider",
            "index": sub_variable
        }
        self.children = []

        sub_variables = SliderTracker.get_sub_variables(variable) 
        assert sub_variables, "error"
        parameters = sub_variables.get_parameters(sub_variable)
        assert parameters, "error"

        for param, ranges in parameters.get_ranges().items():
            self.children.append(html.Label(param))

            min_field = InputField(
                id={
                    "type": "input-slider-min",
                    "index": f"{sub_variable}-{param}"
                },
                type="number", min=-100, max=100, value=ranges.min,
                style={"width": "99%"}
            )
            max_field = InputField(
                id={
                    "type": "input-slider-max",
                    "index": f"{sub_variable}-{param}"
                },
                type="number", min=-100, max=100, value=ranges.max,
                style={"width": "99%"}
            )
            new_slider = Slider(
                # TODO: step calculation -> int=1, float=0.01
                min=ranges.min, max=ranges.max, value=ranges.value, step=0.01,
                marks=None,
                tooltip={"placement": "top", "always_visible": True},
                id={
                    "type": "slider-value",
                    "index": f"{sub_variable}-{param}"
                }
            )
            self.children.append(
                dbc.Row([
                    dbc.Col(min_field, width=1),
                    dbc.Col(new_slider),
                    dbc.Col(max_field, width=1)
                ])
            )


class DistributionComponent(html.Div):
    def __init__(self, variable: str):
        super().__init__()
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.id = variable
        self.children = []

        sub_variables = SliderTracker.get_sub_variables(variable)
        assert sub_variables, "error"
        self.children.extend([
            dbc.Row(html.Label(f"{variable}")),
            html.Hr()
        ])
        for sub_variable, parameters in sub_variables.get_sub_variables().items():
            self.children.append(
                html.Div(
                    style={
                        "border": "2px black solid",
                        "margin": "2px",
                    },
                    children=[
                        html.Label(sub_variable),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col(html.Label("Distribution: "), width="auto"),
                            dbc.Col(
                                Dropdown(
                                    id={
                                        "type": "distribution-options",
                                        "index": sub_variable
                                    },
                                    options=list(DISTRIBUTION_MAPPING.keys()),
                                    value=parameters.distribution_type
                                )
                            )
                        ]),
                        dbc.Row(
                            dbc.Col(
                                html.Div(
                                    id={
                                        "type": "slider-container",
                                        "index": sub_variable
                                    },
                                    children=DistributionSlider(
                                        variable=variable, sub_variable=sub_variable
                                    )
                                )
                            )
                        ),
                        html.Button(
                            children="remove",
                            id={"type": "remove-mixture", "index": variable}
                        )
                    ])
            )
        self.children.append(
            html.Button(
                children="mixture",
                id={"type": "mixture-button", "index": variable}
            )
        )


class DistributionBuilderComponent(html.Div):
    # TODO: this class needs a callback -> when nodes added/deleted/updated
    def __init__(self, id, graph_builder_comp: GraphBuilderComponent):
        super().__init__(id=id)
        # TODO: this singleton controls all distribution components; like graph
        self.children = "empty"
        self.nodes = graph_builder_comp.graph_builder.graph
        # initial nodes init -> a, b
        for node in self.nodes.keys():
            SliderTracker.add_new_variable(node)
        self.update()


    def add_node(self):
        variables = SliderTracker.get_variables().keys()
        diff = set(self.nodes.keys()).difference(variables)
        assert diff and len(diff) == 1, "error"
        to_add = list(diff)[0]
        SliderTracker.add_new_variable(to_add)
        self.update()

    def remove_node(self):
        variables = SliderTracker.get_variables().keys()
        diff = set(variables).difference(set(self.nodes.keys()))
        assert diff and len(diff) == 1, "error"
        to_remove = list(diff)[0]
        SliderTracker.remove_variable(to_remove)
        self.update()

    def update(self):
        self.children = []
        for node in self.nodes.keys():
            self.children.append(DistributionComponent(node))


distribution_builder_component = DistributionBuilderComponent(
    id="distribution-builder-component",
    graph_builder_comp=graph_builder_component
)


# class DistributionViewComponent(html.Div):
#     NR_POINTS = 300
#     def __init__(self, id, var):
#         # TODO: seed set via input
#         np.random.seed(0)
#         # TODO: naming
#         super().__init__()
#         self.id = {"type": "distr_graph", "index": id}
#         values = SliderTracker.get_parameters(var)
#         assert values, "error"
#         value_dict = dict(map(lambda y: (y[0], y[1].value), values.parameter_names.items()))
#         distribution_info = DistributionModelTracker.get_variable(var)
#         assert distribution_info, "error"
#         generator = distribution_info.generator
#         data = generator.rvs(**value_dict, size=DistributionViewComponent.NR_POINTS)
#         fig = ff.create_distplot([data], [id], show_rug=False, curve_type="kde")
#         self.children = Graph(id=f"graph-{id}", figure=fig)
#         self.style = {
#             "border": "2px black solid",
#             "margin": "2px",
#         }
#
#
# class DistributionViewContainer(html.Div):
#     def __init__(self, id):
#         super().__init__(id=id)
#         self.children = []
#         self.children.append(
#             html.Button(id="update_button", children="update")
#         )
#         self.children.extend(
#             [DistributionViewComponent(id=x, var=x)
#                 # for x in DISTRIBUTION_CHOICE_TRACKER.keys()]
#                 for x in DistributionModelTracker.variables.keys()]
#         )
#
#     def update(self):
#         self.children = []
#         self.children.append(
#             html.Button(id="update_button", children="update")
#         )
#         self.children.extend(
#             [DistributionViewComponent(id=x, var=x)
#                 for x in DistributionModelTracker.variables.keys()]
#         )
#
# distribution_view = DistributionViewContainer(id="distr_view")


# slider specific callbacks

@callback(
    Output({"type": "slider-value", "index": MATCH}, "min"),
    Output({"type": "slider-value", "index": MATCH}, "max"),
    Output({"type": "slider-value", "index": MATCH}, "value"),
    Output({"type": "slider-value", "index": MATCH}, "tooltip"),
    Output({"type": "input-slider-min", "index": MATCH}, "value"),
    Output({"type": "input-slider-max", "index": MATCH}, "value"),
    Input({"type": "slider-value", "index": MATCH}, "value"),
    Input({"type": "input-slider-min", "index": MATCH}, "value"),
    Input({"type": "input-slider-max", "index": MATCH}, "value"),
    State({"type": "slider-value", "index": MATCH}, "id"),
    State({"type": "slider-value", "index": MATCH}, "tooltip"),
    prevent_initial_call=True
)
def slider_update(value_, min_, max_, id_, tooltip_):
    sub_variable, param = id_.get("index").split("-")
    variable = sub_variable.split("_")[0]

    sub_variables = SliderTracker.get_sub_variables(variable)
    assert sub_variables, "error1"
    parameters = sub_variables.get_parameters(sub_variable)
    assert parameters, "error2"
    ranges = parameters.get_range(param)
    assert ranges, "error3"
    min_ = min(min_, max_-1)
    value_ = max(value_, min_)
    value_ = min(value_, max_)
    ranges.value = value_
    ranges.min = min_
    ranges.max = max_

    return min_, max_, value_, tooltip_, min_, max_

@callback(
    Output({"type": "slider-container", "index": MATCH}, "children"),
    Input({"type": "distribution-options", "index": MATCH}, "value"),
    Input({"type": "slider-container", "index": MATCH}, "id"),
    prevent_initial_call=True
)
def distribution_choice_update(choice: str, id_: dict):
    sub_variable_name = id_.get("index")
    assert sub_variable_name, "error"
    variable_name = sub_variable_name.split("_")[0]
    sub_variable = SliderTracker.get_sub_variables(variable_name)
    assert sub_variable, "error"

    new_params = ParameterTracker(choice)
    sub_variable.set_distribution(sub_variable_name, new_params)
    updated_slider = DistributionSlider(sub_variable_name, variable_name)

    return updated_slider

#
# @callback(
#     Output("distr_view", "children", allow_duplicate=True),
#     Input("update_button", "n_clicks"),
#     # prevent_initial_call=True
# )
# def udpate_view(_):
#     if ctx.triggered_id == "update_button":
#         distribution_view.update()
#     return distribution_view.children
#
# @callback(
#     Output("distr_view", "children", allow_duplicate=True),
#     Input("distribution-builder-component", "children"),
#     # prevent_initial_call=True
# )
# def udpate_view_2(_):
#     return distribution_view.children
#
