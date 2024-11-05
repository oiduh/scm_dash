import dash_bootstrap_components as dbc
import plotly.figure_factory as ff
from dash import html
from dash.dcc import Dropdown, Graph, Input, Slider

from models.graph import graph
from models.noise import Distribution


class NoiseBuilder(html.Div):
    def __init__(self):
        super().__init__(id="noise-builder")
        self.children = []
        accordion = dbc.Accordion(start_collapsed=True)
        accordion.children = []
        for name in graph.get_node_names():
            accordion.children.append(
                dbc.AccordionItem(NoiseContainer(name), title=name)
            )
        self.children.append(accordion)


class NoiseContainer(html.Div):
    def __init__(self, id_: str):
        super().__init__(id={"type": "noise-container", "index": id_})
        node = graph.get_node_by_id(id_)
        if node is None:
            raise Exception("Node not found")

        self.children = []
        accordion = dbc.Accordion(start_collapsed=True)
        accordion.children = []
        for distribution in node.noise.get_distributions():
            if distribution is None:
                continue
            var_id = distribution.id_
            title = f"{id_}_{var_id}"
            accordion.children.append(
                dbc.AccordionItem(NoiseNodeBuilder((id_, var_id)), title=title)
            )
        self.children.append(accordion)
        self.children.append(
            dbc.Row(
                [
                    dbc.Col(
                        html.Button(
                            "Add distribution",
                            id={"type": "add-sub-distribution", "index": id_},
                        )
                    ),
                ]
            )
        )


class NoiseNodeBuilder(html.Div):
    def __init__(self, id_: tuple[str, str]):
        new_id_ = f"{id_[0]}_{id_[1]}"
        super().__init__(id={"type": "noise-node-builder", "index": new_id_})
        source_node = graph.get_node_by_id(id_[0])
        if source_node is None:
            raise Exception("Source node not found")

        distribution = source_node.noise.get_distribution_by_id(id_[1])
        if distribution is None:
            raise Exception("No parameters found")

        col = dbc.Col()
        col.children = []
        parmeter_options = Distribution.parameter_options()
        col.children.append(
            Dropdown(
                options=parmeter_options,
                value=distribution.name,
                id={"type": "distribution-choice", "index": new_id_},
            )
        )
        col.children.append(html.Hr())
        for param in distribution.parameters.values():
            col.children.append(
                dbc.Col(
                    [
                        dbc.Row(html.H3(param.name)),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Label("slider min: "),
                                        Input(
                                            id={
                                                "type": "input-min",
                                                "index": f"{new_id_}_{param.name}",
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
                                        Input(
                                            id={
                                                "type": "input-value",
                                                "index": f"{new_id_}_{param.name}",
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
                                        Input(
                                            id={
                                                "type": "input-max",
                                                "index": f"{new_id_}_{param.name}",
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
                            Slider(
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
                                    "index": f"{new_id_}_{param.name}",
                                },
                            ),
                            style={"margin-top": "5%"},
                            class_name="h-70",
                            align="end",
                        ),
                    ]
                )
            )
            col.children.append(html.Hr())

        col.children.append(
            html.Button(
                "Remove distribution",
                id={"type": "remove-sub-distribution", "index": new_id_},
            )
        )
        self.children = [col]


class NoiseViewer(html.Div):
    # TODO: hardcoded 'a' since initially defined
    SELECTED_NODE_ID: str = "a"
    def __init__(self):
        super().__init__(id="noise-viewer")

        source_node = graph.get_node_by_id(NoiseViewer.SELECTED_NODE_ID)
        if source_node is None:
            raise Exception("Node not found")

        noise = source_node.noise
        param = noise.id_

        figure = ff.create_distplot(
            [noise.generate_data()], [param], show_rug=False, bin_size=0.2
        )
        self.children = [
            Dropdown(
                options=graph.get_node_ids(),
                searchable=False,
                id="noise-viewer-target",
                multi=False,
            ),
            html.H3(f"variable: {param}"),
            Graph("graph-0", figure=figure)
        ]
