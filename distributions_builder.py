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

class DistributionsEntry(NamedTuple):
    distribution_class: RVCont | RVDisc
    # TODO: range mapping to replace list?
    values: Dict[KWARGS, List]

DISTRIBUTION_MAPPING: Dict[str, DistributionsEntry] = {
    # continuous
    "normal": DistributionsEntry(
        distribution_class=stats.norm,
        values={
            "loc": [],
            "scale": []
        }
    ),
    "lognorm": DistributionsEntry(
        distribution_class=stats.lognorm,
        values={
            "loc": [],
            "scale": [],
            "s": []
        }
    ),
    "uniform": DistributionsEntry(
        distribution_class=stats.uniform,
        values={
            "loc": [],
            "scale": []
        }
    ),
    "laplace": DistributionsEntry(
        distribution_class=stats.laplace,
        values={
            "loc": [],
            "scale": []
        }
    ),
    # discrete
    "poisson": DistributionsEntry(
        distribution_class=stats.laplace,
        values={
            "mu": []
        }
    ),
    "binom": DistributionsEntry(
        distribution_class=stats.binom,
        values={
            "n": [],
            "p": []
        }
    ),
    "bernoulli": DistributionsEntry(
        distribution_class=stats.bernoulli,
        values={
            "p": []
        }
    ),
    "randint": DistributionsEntry(
        distribution_class=stats.randint,
        values={
            "low": [],
            "high": []
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
        global distributions_builder
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

    match input:
        case "normal":
            x = distr(**{
                "loc": 3.0,
                "scale": 3.5
            })
        case "lognorm":
            x = distr(**{
                "loc": 3.0,
                "scale": 2.0,
                "s": 0.9
            })
        case "binom":
            x = distr(**{
                "loc": 3.0,
                "p": 0.5,
                "n": 3
            })
        case _:
            raise Exception("wtf2")

    fig = px.histogram(x=x.rvs(size=300))
    return fig


