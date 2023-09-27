from typing import Dict, Literal, NamedTuple, List

from dash import html, callback, Input, Output, State, ALL, MATCH
from dash.dcc import Dropdown, Graph, Checklist
import plotly.express as px

from graph_builder import graph_builder_component

import scipy.stats as stats
from scipy.stats._distn_infrastructure import rv_frozen as RVFrozen
from scipy.stats import rv_continuous as RVCont, rv_discrete as RVDisc

import numpy as np

KWARGS = Literal["loc", "scale", "s", "mu", "n", "p", "low", "high"]

class Range(NamedTuple):
    min: int | float
    max: int | float
    step: int | float

class DistributionsEntry(NamedTuple):
    distribution_class: RVCont | RVDisc
    values: Dict[KWARGS, Range]

DISTRIBUTION_MAPPING: Dict[str, DistributionsEntry] = {
    # continuous
    "normal": DistributionsEntry(
        distribution_class=stats.norm,
        values={
            "loc": Range(min=-10.0, max=10.0, step=0.5),
            "scale": Range(min=0.0, max=5.0, step=0.1)
        }
    ),
    "lognorm": DistributionsEntry(
        distribution_class=stats.lognorm,
        values={
            "loc": Range(min=-10.0, max=10.0, step=0.5),
            "scale": Range(min=0.0, max=5.0, step=0.1),
            "s": Range(min=0.0, max=5.0, step=0.1)
        }
    ),
    "uniform": DistributionsEntry(
        distribution_class=stats.uniform,
        values={
            "loc": Range(min=-10.0, max=10.0, step=0.5),
            "scale": Range(min=0.0, max=5.0, step=0.1)
        }
    ),
    "laplace": DistributionsEntry(
        distribution_class=stats.laplace,
        values={
            "loc": Range(min=-10.0, max=10.0, step=0.5),
            "scale": Range(min=0.0, max=5.0, step=0.1)
        }
    ),
    # discrete
    "poisson": DistributionsEntry(
        distribution_class=stats.poisson,
        values={
            "mu": Range(min=0.0, max=10.0, step=0.1)
        }
    ),
    "binom": DistributionsEntry(
        distribution_class=stats.binom,
        values={
            "n": Range(min=2, max=10, step=1),
            "p": Range(min=0.0, max=1.0, step=0.05)
        }
    ),
    "bernoulli": DistributionsEntry(
        distribution_class=stats.bernoulli,
        values={
            "p": Range(min=0.0, max=1.0, step=0.05)
        }
    ),
    "randint": DistributionsEntry(
        distribution_class=stats.randint,
        values={
            "low": Range(min=1, max=20, step=1),
            "high": Range(min=2, max=21, step=1)
        }
    )
}

# TODO: dynamic sliders -> depending on variable continuous or discrete
#       min and max of slider adjustable -> low range = more precision

# df = create_data(distr_x=distr_x, distr_y=distr_y, distr_z=distr_z,
#                  kwargs_x=kwargs_x, kwargs_y=kwargs_y, kwargs_z=kwargs_z,
#                  mechanism=mechanism)
# fig = px.scatter(df, x='x', y='y', color='color')
# fig.update_layout(autosize=False, height=800, width=1000)
# # TODO: add option -> equal scale and fill
# assert isinstance(fig.layout, Layout), "type checking"
# assert isinstance(fig.layout.yaxis, YAxis), "type checking"
# fig.layout.yaxis.scaleanchor = 'x'
# return fig, n_clicks

class DistributionComponent(html.Div):
    def __init__(self, id, node) -> None:
        global DISTRIBUTION_MAPPING
        super().__init__(id=id)
        self.distribution = DISTRIBUTION_MAPPING["normal"]
        self.children = [
            html.P(f"variable: {node}"),
            Dropdown(
                id={"type": "distribution-dropdown", "index": node},
                options=list(DISTRIBUTION_MAPPING.keys()),
                value="normal"
            ),
            Checklist(
                id={"type": "show-distribution", "index": node},
                options=["show"], value=[None]
            ),
            html.Div(
                id={"type": "distribution-preview", "index": node},
                children=[
                    Graph(
                        figure={},
                        id={"type": "distribution-graph", "index": node},
                    )
                ],
                style={"display": "none"}
            )
        ]
        self.style={
            'border': '2px black solid',
            'margin': '2px',
        }


class DistributionsBuilderComponent(html.Div):
    def __init__(self, id):
        super().__init__(id=id)
        self.style = {
            'border': '2px black solid',
            'margin': '2px'
        }
        self.children = "DistributionsComponent"

distributions_builder_component = DistributionsBuilderComponent(
    id="distributions-builder-component"
)

@callback(
    Output("distributions-builder-component", "children", allow_duplicate=True),
    Input("node-container", "children"),
    prevent_initial_call="initial_duplicate"
)
def add_node(_):
    ret = []
    nodes = graph_builder_component.graph_builder.graph.keys()
    for node in nodes:
        print(node)
        new_component = DistributionComponent(
            id=f"distribution-node-{node}",
            node=node
        )
        ret.append(new_component)
    return ret

@callback(
    Output({"type": "distribution-preview", "index": MATCH}, "style"),
    Input({"type": "show-distribution", "index": MATCH}, "value"),
    prevent_initial_call=True
)
def preview_graph(input):
    input = list(filter(lambda x: x is not None, input))
    if not input:
        return {"display": "none"}
    else:
        return {"display": "block"}

@callback(
    Output({"type": "distribution-graph", "index": MATCH}, "figure"),
    Input({"type": "distribution-dropdown", "index": MATCH}, "value"),
)
def test_abc(input):
    global DISTRIBUTION_MAPPING
    distr = DISTRIBUTION_MAPPING.get(input)
    if not distr:
        raise Exception("wtf")
    assert distr is not None, "wtf"

    c = {k: v.max for k, v in distr.values.items()}
    d = distr.distribution_class(**c)

    fig = px.histogram(x=d.rvs(size=300))
    return fig


