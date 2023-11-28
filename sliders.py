from dash import callback, html, Output, Input, State, ALL, MATCH, ctx
from dash.dcc import RadioItems, Slider, Input as InputField, Dropdown, Graph
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from distributions_builder import(
    DISTRIBUTION_MAPPING, Generator, DEFAULT_DISTRIBUTION
)
from typing import Optional, Dict, Literal
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
        self.parameter_names.update({parameter: ranges})


class SubVariableTracker:
    def __init__(self, variable: str) -> None:
        self.variable = variable
        self.sub_variables: Dict[str, ParameterTracker] = {}
        self.counter = 0
        self.visibility: Literal["hide", "show"] = "show"

    def get_sub_variables(self):
        return self.sub_variables

    def get_parameters(self, sub_variable: str):
        return self.sub_variables.get(sub_variable)

    def add_distribution(self):
        self.counter += 1
        new_params = ParameterTracker(DEFAULT_DISTRIBUTION[0])
        self.sub_variables.update({f"{self.variable}_{self.counter}": new_params})

    def set_distribution(self, sub_var_name: str, params: ParameterTracker):
        self.sub_variables.update({sub_var_name: params})

    def remove_sub_variable(self, sub_variable: str):
        assert self.sub_variables.get(sub_variable), "does not exist"
        if len(self.sub_variables.keys()) > 1:
            return self.sub_variables.pop(sub_variable, None)
        return None


class SliderTracker:
    variables: Dict[str, SubVariableTracker] = {}
    last_updated: Optional[str] = None

    @staticmethod
    def get_variables():
        return SliderTracker.variables

    @staticmethod
    def get_sub_variables(variable: str):
        return SliderTracker.variables.get(variable)

    @staticmethod
    def add_new_variable(variable: str):
        new_distr = SubVariableTracker(variable)
        new_distr.add_distribution()
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
        self.id = {"type": "variable-container", "index": variable}
        self.children = []

        sub_variables = SliderTracker.get_sub_variables(variable)
        assert sub_variables, "error"
        self.children.extend([
            dbc.Row(html.Label(f"{variable}")),
            html.Hr()
        ])
        self.children.append(
            RadioItems(
                id={"type": "variable-visibility", "index": variable},
                options=["hide", "show"], value=sub_variables.visibility,
                inline=True
            )
        )
        sub_variable_container = html.Div(
            id={"type": "all-subvariables", "index": variable},
            style={
                "border": "2px red solid",
                "margin": "2px",
                "display": sub_variables.visibility
            },
        )
        sub_variable_container.children = []
        for sub_variable, parameters in sub_variables.get_sub_variables().items():
            sub_variable_container.children.append(
                html.Div(
                    id={"type": "sub-variable-container", "index": sub_variable},
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
                            id={"type": "remove-mixture", "index": sub_variable},
                            n_clicks=0
                        )
                    ])
            )
        sub_variable_container.children.extend([
            html.Button(
                children="mixture",
                id={"type": "add-mixture", "index": variable},
                n_clicks=0
            ),
            html.Button(
                children="inspect",
                id={"type": "inspect", "index": variable}
            ),
        ])
        self.children.append(sub_variable_container)


class DistributionBuilderComponent(html.Div):
    def __init__(self, id, graph_builder_comp: GraphBuilderComponent):
        super().__init__(id=id)
        self.children = "empty"
        self.graph_builder = graph_builder_comp.graph_builder
        for node in self.graph_builder.graph_tracker.out_edges.keys():
            SliderTracker.add_new_variable(node)
        self.update()

    def add_node(self):
        print("dbc add")
        variables = SliderTracker.get_variables().keys()
        diff = set(self.graph_builder.graph_tracker.out_edges.keys()).difference(variables)
        if diff:
            to_add = list(diff)[0]
            SliderTracker.add_new_variable(to_add)
            self.update()

    def remove_node(self):
        print("dbc remove")
        variables = SliderTracker.get_variables().keys()
        diff = set(variables).difference(set(self.graph_builder.graph_tracker.out_edges.keys()))
        if diff:
            # assert diff and len(diff) == 1, "error"
            to_remove = list(diff)[0]
            SliderTracker.remove_variable(to_remove)
            self.update()

    def update(self):
        print("dbc update")
        self.children = []
        for node in self.graph_builder.graph_tracker.out_edges.keys():
            self.children.append(DistributionComponent(node))


distribution_builder_component = DistributionBuilderComponent(
    id="distribution-builder-component",
    graph_builder_comp=graph_builder_component
)


class DistributionViewContainer(html.Div):
    # TODO: make NR_POINTS configurable
    NR_POINTS = 1333
    def __init__(self, id):
        super().__init__(id=id)
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.children = "empty"

    @staticmethod
    def create_graphs(variable_name: str):
        # TODO: make function to set or refresh seed
        np.random.seed(0)
        variable = SliderTracker.get_sub_variables(variable_name)
        assert variable, "error"
        sub_variables = variable.get_sub_variables()
        sub_variable_count = len(sub_variables)
        partition, rest = divmod(DistributionViewContainer.NR_POINTS, sub_variable_count)
        x = [partition for _ in range(sub_variable_count)]
        y = [1 if idx < rest else 0 for idx, _ in enumerate(range(sub_variable_count))]
        z = [a + b for a, b in zip(x,y)]
        data_container, sub_variable_names, distribution_types = [], [], []
        for (sub_variable, parameters), nr_points in zip(sub_variables.items(), z):
            distribution_types.append(parameters.distribution_type)
            sub_variable_names.append(sub_variable)
            generator = parameters.generator
            value_dict = dict(map(lambda x: (x[0], x[1].value), parameters.get_ranges().items()))
            data = generator.rvs(**value_dict, size=nr_points)
            data_container.append(data)

        # graph with individual components
        legend = list(map(lambda x: f"{x[0]}, {x[1]}", zip(sub_variable_names, distribution_types)))
        fig_1 = ff.create_distplot(data_container, legend, show_rug=False, curve_type="kde")

        # graph with combined components
        data_container_2 = [x for y in data_container for x in y]
        fig_2 = ff.create_distplot([data_container_2], [variable_name], show_rug=False, curve_type="kde")

        return [Graph(figure=fig_1), Graph(figure=fig_2)]

distribution_view = DistributionViewContainer(id="test-graph")


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

    SliderTracker.last_updated = variable

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

@callback(
    Output({"type": "variable-container", "index": MATCH}, "children",
           allow_duplicate=True),
    Input({"type": "add-mixture", "index": MATCH}, "n_clicks"),
    State({"type": "variable-container", "index": MATCH}, "id"),
    prevent_initial_call=True
)
def add_mixture(button_, id_):
    if button_ == 0:
        raise PreventUpdate
    index = id_.get("index")
    assert index, "error"
    variable = index.split("_")[0]
    sub_variables = SliderTracker.get_sub_variables(variable)
    assert sub_variables, "error"
    sub_variables.add_distribution()

    return DistributionComponent(variable).children


@callback(
    Output({"type": "variable-container", "index": ALL}, "children",
           allow_duplicate=True),
    Output({"type": "remove-mixture", "index": ALL}, "n_clicks"),
    Input({"type": "remove-mixture", "index": ALL}, "n_clicks"),
    State({"type": "variable-container", "index": ALL}, "children"),
    prevent_initial_call=True
)
def remove_mixture(button_, state_):
    triggered_button = ctx.triggered_id
    assert triggered_button is not None, "error"
    sub_variable_name: str = triggered_button.get("index", None)
    assert sub_variable_name and isinstance(sub_variable_name, str), "error"
    variable_name = sub_variable_name.split("_")
    assert variable_name, "error"
    variable_name = variable_name[0]

    index = list(SliderTracker.get_variables().keys())
    index = index.index(variable_name)

    if sum(button_) == 0:
        raise PreventUpdate

    variable = SliderTracker.get_sub_variables(variable_name)
    assert variable, "error"
    if not variable.remove_sub_variable(sub_variable_name):
        return state_, [0 for _ in range(len(button_))]

    updated_variable = DistributionComponent(variable_name)
    state_[index] = updated_variable.children

    return state_, [0 for _ in range(len(button_))]

@callback(
    Output("test-graph", "children", allow_duplicate=True),
    Input({"type": "inspect", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def inspect_distribution(_):

    triggered_button = ctx.triggered_id
    if not triggered_button:
        raise PreventUpdate


    variable_name = triggered_button.get("index")
    assert variable_name, "error"

    return DistributionViewContainer.create_graphs(variable_name)

@callback(
    Output({"type": "all-subvariables", "index": MATCH}, "style"),
    Input({"type": "variable-visibility", "index": MATCH}, "value"),
    State({"type": "all-subvariables", "index": MATCH}, "style"),
    State({"type": "all-subvariables", "index": MATCH}, "id")
)
def trigger_visibility(visibility_option: str, current_style: dict, id_: dict):
    variable_name = id_.get("index")
    assert variable_name, "error"
    variable = SliderTracker.get_sub_variables(variable_name)
    assert variable, "error"
    if visibility_option == "show":
        variable.visibility = "show"
        current_style.update({"display": "block"})
    else:
        variable.visibility = "hide"
        current_style.update({"display": "none"})
    return current_style

@callback(
    Output("test-graph", "children"),
    Input({"type": "slider-value", "index": ALL}, "value"),
    State("test-graph", "children"),
    prevent_initial_call=True
)
def graph_sync(_, current_state):
    last_updated = SliderTracker.last_updated
    if last_updated:
        return DistributionViewContainer.create_graphs(last_updated)
    else:
        return current_state
