from typing import Dict, Literal, NamedTuple, List, Type, Union

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
    init: int | float
    step: int | float
    num_type: Literal["int", "float"]

class DistributionsEntry(NamedTuple):
    distribution_class: RVCont | RVDisc
    values: Dict[KWARGS, Range]

DISTRIBUTION_MAPPING: Dict[str, DistributionsEntry] = {
    # continuous
    "normal": DistributionsEntry(
        distribution_class=stats.norm,
        values={
            "loc": Range(min=-10.0, max=10.0, init=0.0, step=0.5, num_type="float"),
            "scale": Range(min=0.0, max=5.0, init=1.0, step=0.1, num_type="float")
        },
    ),
    "lognorm": DistributionsEntry(
        distribution_class=stats.lognorm,
        values={
            "loc": Range(min=-10.0, max=10.0, init=1.0, step=0.5, num_type="float"),
            "scale": Range(min=0.0, max=5.0, init=1.0, step=0.1, num_type="float"),
            "s": Range(min=0.0, max=5.0, init=0.5, step=0.1, num_type="float")
        }
    ),
    "uniform": DistributionsEntry(
        distribution_class=stats.uniform,
        values={
            "loc": Range(min=-10.0, max=10.0, init=0.0, step=0.5, num_type="float"),
            "scale": Range(min=0.0, max=5.0, init=1.0, step=0.1, num_type="float")
        }
    ),
    "laplace": DistributionsEntry(
        distribution_class=stats.laplace,
        values={
            "loc": Range(min=-10.0, max=10.0, init=0.0, step=0.5, num_type="float"),
            "scale": Range(min=0.0, max=5.0, init=1.0, step=0.1, num_type="float")
        }
    ),

    # discrete
    "poisson": DistributionsEntry(
        distribution_class=stats.poisson,
        values={
            "mu": Range(min=0.0, max=10.0, init=1.0, step=0.1, num_type="float")
        }
    ),
    "binom": DistributionsEntry(
        distribution_class=stats.binom,
        values={
            "n": Range(min=2, max=10, init=2, step=1, num_type="int"),
            "p": Range(min=0.0, max=1.0, init=0.5, step=0.05, num_type="float")
        }
    ),
    "bernoulli": DistributionsEntry(
        distribution_class=stats.bernoulli,
        values={
            "p": Range(min=0.0, max=1.0, init=0.5, step=0.05, num_type="float")
        }
    ),
    "randint": DistributionsEntry(
        distribution_class=stats.randint,
        values={
            "low": Range(min=1, max=20, init=1, step=1, num_type="int"),
            "high": Range(min=2, max=21, init=5, step=1, num_type="int")
        }
    )
}

