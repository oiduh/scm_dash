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
        print([x.id for x in node.data.get_distributions()])
        self.children = []
        accordion = dbc.Accordion(always_open=True)
        accordion.children = []
        for distribution in node.data.get_distributions():
            var_id = distribution.id
            title = f"{id}_{var_id}"
            accordion.children.append(dbc.AccordionItem(NoiseNodeBuilder((id, var_id)), title=title))
        self.children.append(accordion)


class NoiseNodeBuilder(html.Div):
    def __init__(self, id: tuple[str, str]):
        super().__init__(id=f"{id[0]}_{id[1]}")
        distr = graph.get_node_by_id(id[0]).data.get_distribution_by_id(id[1])
        assert distr, "no params"

        col = dbc.Col()
        col.children = []
        parmeter_options = Distribution.parameter_options()
        col.children.append(Dropdown(options=parmeter_options, value=parmeter_options[0]))
        col.children.append(html.Hr())
        for idx, param in enumerate(distr.parameters.values()):
            col.children.append(dbc.Col([
                dbc.Row(dbc.Col(param.name, width=1)),
                dbc.Row([
                    dbc.Col(["current", Input(type="number", size="10")]), 
                    dbc.Col(["start", Input(type="number", size="15")]),
                    dbc.Col(["end", Input(type="number", size="20")]),
                ]),
                dbc.Row(Slider(
                    min=param.min, max=param.max, step=param.step, value=param.current,
                    marks={param.min: str(param.min), param.max: str(param.max)},
                    tooltip={"placement": "bottom", "always_visible": True},
                    id={
                        "type": "slider-value",
                        "index": f"{id[0]}-{id[1]}-{param.name}"
                    }
                ))
            ]))
            if idx != len(distr.parameters) - 1:
                col.children.append(html.Hr())

        self.children = [col]


class NoiseViewer(html.Div):
    def __init__(self):
        super().__init__(id="noise-viewer")
        self.children = []

