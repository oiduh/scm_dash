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
        self.parameter_names: Dict[str, RangeTracker] = dict()
        distribution = DISTRIBUTION_MAPPING.get(distribution_type)
        assert distribution, "error"
        self.generator: Generator = distribution.generator

    def get_distribution_type(self):
        return self.distribution_type

    def get_parameter(self, parameter: str):
        return self.parameter_names.get(parameter)

    def set_parameter(self, parameter: str, ranges: RangeTracker):
        self.parameter_names.update({
            parameter: ranges
        })


class DistributionTracker:
    def __init__(self) -> None:
        self.distributions: Dict[str, ParameterTracker] = {}

    def get_parameters(self):
        return self.distributions

    def get_parameter(self, param: str):
        return self.distributions.get(param)

    def set_distribution(self, var_name: str, params: ParameterTracker):
        self.distributions.update({var_name: params})


class SliderTracker:
    variable_names: Dict[str, DistributionTracker] = {}

    @staticmethod
    def get_distributions():
        return SliderTracker.variable_names

    @staticmethod
    def get_distribution(variable: str):
        return SliderTracker.variable_names.get(variable)

    @staticmethod
    def add_new_variable(variable: str):
        new_distr = DistributionTracker()
        new_params = ParameterTracker(DEFAULT_DISTRIBUTION[0])
        for param, ranges in DEFAULT_DISTRIBUTION[1].values.items():
            new_range = RangeTracker(ranges.min, ranges.max, ranges.init)
            new_params.set_parameter(param, new_range)
        new_distr.set_distribution(f"{variable}_1", new_params)
        SliderTracker.variable_names.update({variable: new_distr})

    @staticmethod
    def remove_variable(variable: str):
        assert SliderTracker.variable_names.get(variable) is not None, "error"
        SliderTracker.variable_names.pop(variable)

    @staticmethod
    def show():
        for x, y in SliderTracker.variable_names.items():
            print(f"{x}:")
            for a, b in y.get_parameters().items():
                print(f"  {a} ({b.distribution_type}):")
                for c, d in b.parameter_names.items():
                    print(f"    {c}")
                    print(f"      {d.min}")
                    print(f"      {d.max}")
                    print(f"      {d.value}")


class DistributionSlider(html.Div):

    def __init__(self, id):
        super().__init__(id=id)
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.variable_name = id
        self.id = {
            "type": "slider-content",
            "index": id
        }
        # TODO: proper layout -> 
        # need:
        #       div for variable
        #       div for each part of the mixture mode
        #       button to add another mixture model
        self.children = []

    def update(self):
        self.children = []
        if not SliderTracker.variable_names:
            self.children.append("empty")
            return



        if (m:=SliderTracker.get_distributions(self.variable_name)) and (n:=m.get_parameters()):
            distr_names = [o.distribution_type for o in n.values()]
            values = [o.parameter_names for o in n.values()]
        else:
            distr_name = DEFAULT_DISTRIBUTION[0]
            values = ParameterTracker(distr_name)
            for kwargs_, ranges_ in DEFAULT_DISTRIBUTION[1].values.items():
                ranges = RangeTracker(ranges_.min, ranges_.max, ranges_.init)
                values.set_parameter(kwargs_, ranges)
            distr_names = [distr_name]
            values = [values]


        self.children = []
        for param, initial_values in values.parameter_names.items():
        # for param, initial_values in distribution_values.items():
            slider_content = dbc.Col()
            slider_content.children = []
            slider_content.children.append(dbc.Row(dbc.Col(html.Label(param)), align="center"))

            sliders = dbc.Row()
            sliders.children = []

            parmeter_values = SliderTracker.get_parameters(id)
            if parmeter_values and (ranges:=parmeter_values.get_parameter(param)):
                min_ = ranges.min
                max_ = ranges.max
                value_ = ranges.value
            else:
                min_ = initial_values.min
                max_ = initial_values.max
                value_ = initial_values.value
                ranges = RangeTracker(min_, max_, value_)
                if m:=SliderTracker.get_parameters(id):
                    m.set_parameter(param, ranges)
                else:
                    new_param = ParameterTracker(distr_name)
                    new_param.set_parameter(param, ranges)
                    SliderTracker.set_value_parameters(id, new_param)

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
            # TODO: error should vanish once DISTRIBUTION_MAPPING reworked to model
            num_type = DISTRIBUTION_MAPPING.get(distr_name)
            assert num_type, "error"
            num_type = num_type.values.get(param)
            assert num_type, "error"
            num_type = num_type.num_type

            step = 1 if num_type == "int" else 0.01
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
        if m:=DistributionModelTracker.get_variable(id):
            gen = m.generator
            name = m.name
        else:
            gen = DEFAULT_DISTRIBUTION[1].generator
            name = DEFAULT_DISTRIBUTION[0]
        DistributionModelTracker.update_distribution(
            id, DistributionGenerator(name, gen)
        )
        self.children.extend([
            dbc.Row(html.Label(f"Variable: {id}")),
            html.Hr(),
            # TODO: make new component here
            dbc.Row([
                dbc.Col(html.Label("Distribution: "), width="auto"),
                dbc.Col(
                    Dropdown(
                        id={
                            "type": "distribution-options",
                            "index": id
                        },
                        options=list(DISTRIBUTION_MAPPING.keys()),
                        value=name
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
            ),
            html.Button(children="aaaa", id={"type": "some-button", "index": id})
        ])


class DistributionBuilderComponent(html.Div):
    # TODO: this class needs a callback -> when nodes added/deleted/updated
    def __init__(self, id, graph_builder_comp: GraphBuilderComponent):
        super().__init__(id=id)
        # TODO: this singleton controls all distribution components; like graph
        self.children: List[DistributionComponent] = []
        self.nodes = graph_builder_comp.graph_builder.graph
        self.update()

    def add_node(self):
        variables = SliderTracker.get_distributions().keys()
        diff = set(self.nodes.keys()).difference(variables)
        assert diff and len(diff) == 1, "error"
        to_add = list(diff)[0]
        SliderTracker.add_new_variable(to_add)
        self.update()
        
        for node in self.nodes.keys():
            self.children.append(DistributionComponent(node))

    def remove_node(self):
        variables = SliderTracker.get_distributions().keys()
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


class DistributionViewComponent(html.Div):
    NR_POINTS = 300
    def __init__(self, id, var):
        # TODO: seed set via input
        np.random.seed(0)
        # TODO: naming
        super().__init__()
        self.id = {"type": "distr_graph", "index": id}
        values = SliderTracker.get_parameters(var)
        assert values, "error"
        value_dict = dict(map(lambda y: (y[0], y[1].value), values.parameter_names.items()))
        distribution_info = DistributionModelTracker.get_variable(var)
        assert distribution_info, "error"
        generator = distribution_info.generator
        data = generator.rvs(**value_dict, size=DistributionViewComponent.NR_POINTS)
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
                # for x in DISTRIBUTION_CHOICE_TRACKER.keys()]
                for x in DistributionModelTracker.variables.keys()]
        )

    def update(self):
        self.children = []
        self.children.append(
            html.Button(id="update_button", children="update")
        )
        self.children.extend(
            [DistributionViewComponent(id=x, var=x)
                for x in DistributionModelTracker.variables.keys()]
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
    # prevent_initial_call=True
)
def slider_sync(input1, input2, input3, tt, id_):
    node, kwarg = id_.get("index").split("-")
    if (m:=SliderTracker.get_parameters(node)) and m.get_parameter(kwarg):
        new_range = RangeTracker(input1, input2, input3)
        m.set_parameter(kwarg, new_range)
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
    # prevent_initial_call=True
)
def distribution_update(choice: str, id_: dict):
    distribution = DISTRIBUTION_MAPPING.get(choice)
    assert distribution, "distr not found"
    var_name = id_.get("index")
    assert var_name, "no varname"
    DistributionModelTracker.update_distribution(
        var_name, DistributionGenerator(choice, distribution.generator)
    )

    SliderTracker.remove_variable(var_name)
    new_params = ParameterTracker(choice)
    for kwargs_, range_ in distribution.values.items():
        new_range = RangeTracker(range_.min, range_.max, range_.init)
        new_params.set_parameter(kwargs_, new_range)
    SliderTracker.set_value_parameters(var_name, new_params)
    SliderTracker.show()
    new_comp = DistributionSlider(var_name)
    return new_comp

@callback(
    Output("distr_view", "children", allow_duplicate=True),
    Input("update_button", "n_clicks"),
    # prevent_initial_call=True
)
def udpate_view(_):
    if ctx.triggered_id == "update_button":
        distribution_view.update()
    return distribution_view.children

@callback(
    Output("distr_view", "children", allow_duplicate=True),
    Input("distribution-builder-component", "children"),
    # prevent_initial_call=True
)
def udpate_view_2(_):
    return distribution_view.children

