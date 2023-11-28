from typing import Dict, Literal, NamedTuple

import scipy.stats as stats
from scipy.stats import rv_continuous as RVCont, rv_discrete as RVDisc

KWARGS = Literal["loc", "scale", "s", "mu", "n", "p", "low", "high"]
Generator = RVCont | RVDisc

class Range(NamedTuple):
    min: int | float
    max: int | float
    init: int | float
    step: int | float
    num_type: Literal["int", "float"]

class DistributionsEntry(NamedTuple):
    generator: Generator
    values: Dict[KWARGS, Range]

DEFAULT_DISTRIBUTION = (
    "normal",
    DistributionsEntry(
        generator=stats.norm,
        values={
            "loc": Range(min=-10.0, max=10.0, init=0.0, step=0.5, num_type="float"),
            "scale": Range(min=0.0, max=5.0, init=1.0, step=0.1, num_type="float")
        }
    )
)

DISTRIBUTION_MAPPING: Dict[str, DistributionsEntry] = {
    # continuous
    "normal": DistributionsEntry(
        generator=stats.norm,
        values={
            "loc": Range(min=-10.0, max=10.0, init=0.0, step=0.5, num_type="float"),
            "scale": Range(min=0.0, max=5.0, init=1.0, step=0.1, num_type="float")
        },
    ),
    "lognorm": DistributionsEntry(
        generator=stats.lognorm,
        values={
            "loc": Range(min=-10.0, max=10.0, init=1.0, step=0.5, num_type="float"),
            "scale": Range(min=0.0, max=5.0, init=1.0, step=0.1, num_type="float"),
            "s": Range(min=0.0, max=5.0, init=0.5, step=0.1, num_type="float")
        }
    ),
    "uniform": DistributionsEntry(
        generator=stats.uniform,
        values={
            "loc": Range(min=-10.0, max=10.0, init=0.0, step=0.5, num_type="float"),
            "scale": Range(min=0.0, max=5.0, init=1.0, step=0.1, num_type="float")
        }
    ),
    "laplace": DistributionsEntry(
        generator=stats.laplace,
        values={
            "loc": Range(min=-10.0, max=10.0, init=0.0, step=0.5, num_type="float"),
            "scale": Range(min=0.0, max=5.0, init=1.0, step=0.1, num_type="float")
        }
    ),

    # discrete
    "poisson": DistributionsEntry(
        generator=stats.poisson,
        values={
            "mu": Range(min=0.0, max=10.0, init=1.0, step=0.1, num_type="float")
        }
    ),
    "binom": DistributionsEntry(
        generator=stats.binom,
        values={
            "n": Range(min=2, max=10, init=2, step=1, num_type="int"),
            "p": Range(min=0.0, max=1.0, init=0.5, step=0.05, num_type="float")
        }
    ),
    "bernoulli": DistributionsEntry(
        generator=stats.bernoulli,
        values={
            "p": Range(min=0.0, max=1.0, init=0.5, step=0.05, num_type="float")
        }
    ),
    "randint": DistributionsEntry(
        generator=stats.randint,
        values={
            "low": Range(min=1, max=20, init=1, step=1, num_type="int"),
            "high": Range(min=2, max=21, init=5, step=1, num_type="int")
        }
    )
}

