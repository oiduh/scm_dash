import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.figure_factory as ff
import numpy as np

from models.graph import graph
from models.noise import Distribution


# class NoiseBuilder(html.Div):
#     def __init__(self):
#         super().__init__(id="noise-builder")
#         self.children = []
#         accordion = dbc.Accordion(start_collapsed=True)
#         accordion.children = []
#         for name in graph.get_node_names():
#             accordion.children.append(
#                 dbc.AccordionItem(NoiseContainer(name), title=name)
#             )
#         self.children.append(accordion)
#

class NoiseBuilderNew(html.Div):
    def __init__(self):
        super().__init__(id="noise-builder-new")
        self.children = []
        node_ids = graph.get_node_ids()
        VariableSelection.variable = node_ids[0]
        assert len(node_ids) > 0
        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None
        sub_variables = list(node.noise.sub_distributions.keys())
        assert len(sub_variables) > 0
        VariableSelection.sub_variable = sub_variables[0]
        self.children.append(VariableSelection())
        self.children.append(html.Hr()) # TODO: better distinction from rest
        self.children.append(NoiseConfig())


class VariableSelection(html.Div):
    variable: str
    sub_variable: str
    def __init__(self):
        super().__init__(id="variable-selection-noise")
        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None
        sub_variables = [
            var for var, x in node.noise.sub_distributions.items() if x is not None
        ]

        displayed_names = {node.id_: node.name or node.id_ for node in graph.get_nodes()}

        self.children = []
        self.children.extend([
            dbc.Row(
                dbc.Col(
                    dcc.Dropdown(
                        options=displayed_names,
                        value=VariableSelection.variable,
                        id="noise-builder-variable",
                        searchable=False,
                        clearable=False
                    )
                ),
            ),
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        options=sub_variables,
                        value=VariableSelection.sub_variable,
                        id="noise-builder-sub-variable",
                        searchable=False,
                        clearable=False
                    )
                ),
                dbc.Col(
                    html.Button("Remove selected sub variable", id="remove-sub-variable", n_clicks=0)
                ),
                dbc.Col(
                    html.Button("Add new sub variable", id="add-sub-variable", n_clicks=0)
                )
            ])
        ])


class NoiseConfig(html.Div):
    def __init__(self):
        super().__init__(id="noise-config")
        selected_node = graph.get_node_by_id(VariableSelection.variable)
        assert selected_node is not None
        assert VariableSelection.sub_variable in selected_node.noise.sub_distributions

        distribution = selected_node.noise.sub_distributions.get(VariableSelection.sub_variable)
        assert distribution is not None

        parmeter_options = Distribution.parameter_options()

        self.children = []
        self.children.append(
            dcc.Dropdown(
                options=parmeter_options,
                value=distribution.name,
                id="distribution-choice",
                searchable=False,
                clearable=False
            )
        )
        for param in distribution.parameters.values():
            self.children.append(
                dbc.Col(
                    [
                        dbc.Row(html.H3(param.name)),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("slider min: "),
                                        dcc.Input(
                                            id={
                                                "type": "input-min",
                                                "index": f"{param.name}",
                                            },
                                            value=param.slider_min,
                                            type="number",
                                            size="7",
                                            min=param.min,
                                            max=param.max,
                                            step=param.step,
                                        ),
                                    ],
                                    width=3,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("current: "),
                                        dcc.Input(
                                            id={
                                                "type": "input-value",
                                                "index": f"{param.name}",
                                            },
                                            value=param.current,
                                            type="number",
                                            size="7",
                                            min=param.min,
                                            max=param.max,
                                            step=param.step,
                                        ),
                                    ],
                                    width=3,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Label("slider max: "),
                                        dcc.Input(
                                            id={
                                                "type": "input-max",
                                                "index": f"{param.name}",
                                            },
                                            value=param.slider_max,
                                            type="number",
                                            size="7",
                                            min=param.min,
                                            max=param.max,
                                            step=param.step,
                                        ),
                                    ],
                                    width=3,
                                ),
                            ],
                            class_name="h-30",
                            justify="between",
                        ),
                        dbc.Row(
                            dcc.Slider(
                                min=param.min,
                                max=param.max,
                                step=param.step,
                                value=param.current,
                                marks={
                                    param.min: str(param.min),
                                    param.max: str(param.max),
                                },
                                tooltip={"placement": "top", "always_visible": True},
                                id={
                                    "type": "slider",
                                    "index": f"{param.name}",
                                },
                            ),
                            style={"margin-top": "5%"},
                            class_name="h-70",
                            align="end",
                        ),
                    ]
                )
            )


class NoiseViewer(html.Div):
    def __init__(self):
        super().__init__(id="noise-viewer")

        source_node = graph.get_node_by_id(VariableSelection.variable)
        assert source_node is not None

        noise = source_node.noise
        param = noise.id_

        # TODO: 2 graphs
        # 1) inidiviual sub variable distribution
        # 2) combined distribution
        # 3) save axes option(?)
        self.children = []
        if len(noise.get_distributions()) == 1:
            var_data, _ = noise.generate_data(VariableSelection.sub_variable)
            var_figure = ff.create_distplot(
                [var_data], [param], show_rug=False, bin_size=0.2, colors=["blue"]
            )
            self.children = [
                html.H3(f"variable: {param}"),
                dcc.Graph("graph-var", figure=var_figure),
            ]
        else:
            var_data, sub_var_data = noise.generate_data(VariableSelection.sub_variable)
            var_figure = ff.create_distplot(
                [var_data], [param], show_rug=False, bin_size=0.2, colors=["blue"]
            )
            sub_var_figure = ff.create_distplot(
                [sub_var_data], [VariableSelection.sub_variable], show_rug=False, bin_size=0.2, colors=["red"]
            )
            self.children = [
                html.H3(f"variable: {param}"),
                dcc.Graph("graph-var", figure=var_figure),
                html.H3(f"sub_variable: {VariableSelection.sub_variable}"),
                dcc.Graph("graph-sub-var", figure=sub_var_figure),
            ]

