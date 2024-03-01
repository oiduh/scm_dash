from dash import html
from dash.dcc import Dropdown, Slider, Input
import dash_bootstrap_components as dbc

from models.graph import graph
from models.noise import Distribution


class NoiseBuilder(html.Div):
    def __init__(self):
        super().__init__(id="noise-builder")
        self.children = []
        accordion = dbc.Accordion(always_open=True)
        accordion.children = []
        for name in graph.get_node_names():
            accordion.children.append(dbc.AccordionItem(NoiseContainer(name), title=name))
        self.children.append(accordion)


class NoiseContainer(html.Div):
    def __init__(self, id: str):
        super().__init__(id=id)
        node = graph.get_node_by_id(id)
        self.children = []
        accordion = dbc.Accordion(always_open=True)
        accordion.children = []
        for distribution in node.data.get_distributions():
            var_id = distribution.id
            title = f"{id}_{var_id}"
            accordion.children.append(dbc.AccordionItem(NoiseNodeBuilder((id, var_id)), title=title))
        self.children.append(accordion)
        self.children.append(html.Hr())
        self.children.append(html.Button("Add distribution"))


class NoiseNodeBuilder(html.Div):
    def __init__(self, id: tuple[str, str]):
        id_ = f"{id[0]}_{id[1]}"
        super().__init__(id={"type": "noise-node-builder", "index": id_})
        distr = graph.get_node_by_id(id[0]).data.get_distribution_by_id(id[1])
        assert distr, "no params"

        col = dbc.Col()
        col.children = []
        parmeter_options = Distribution.parameter_options()
        col.children.append(Dropdown(
            options=parmeter_options, value=distr.name,
            id={"type": "distribution-choice", "index": id_}
        ))
        col.children.append(html.Hr())
        for param in distr.parameters.values():
            col.children.append(dbc.Col([
                dbc.Row(html.H3(param.name)),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("slider min: "),
                        Input(
                            id={"type": "input-min", "index": f"{id_}_{param.name}"},
                            value=param.slider_min, type="number", size="7",
                            min=param.min, max=param.max, step=param.step
                        )
                    ], width=3),
                    dbc.Col([
                        dbc.Label("current: "),
                        Input(
                            id={"type": "input-value", "index": f"{id_}_{param.name}"},
                            value=param.current, type="number", size="7",
                            min=param.min, max=param.max, step=param.step
                        )
                    ], width=3), 
                    dbc.Col([
                        dbc.Label("slider max: "),
                        Input(
                            id={"type": "input-max", "index": f"{id_}_{param.name}"},
                            value=param.slider_max, type="number", size="7",
                            min=param.min, max=param.max, step=param.step
                        )
                    ], width=3),
                ], style={"height": 50}, justify="between"),
                dbc.Row(Slider(
                    min=param.min, max=param.max, step=param.step, value=param.current,
                    marks={param.min: str(param.min), param.max: str(param.max)},
                    tooltip={"placement": "top", "always_visible": True},
                    id={
                        "type": "slider",
                        "index": f"{id_}_{param.name}"
                    }
                ), style={"height": 50}, align="end"),
            ]))
            col.children.append(html.Hr())

        col.children.append(html.Button(
            "Remove distribution", id={"type": "remove-distribution", "index": id_}
        ))
        self.children = [col]


class NoiseViewer(html.Div):
    def __init__(self):
        super().__init__(id="noise-viewer")
        self.children = []

