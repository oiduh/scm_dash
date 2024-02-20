from typing import Dict, Literal, NamedTuple
import scipy.stats as stats
from scipy.stats import rv_continuous as RVCont, rv_discrete as RVDisc
import numpy as np


Generator = RVCont | RVDisc



class CONSTANTS:
    NR_DATA_POINTS = 2000


KWARGS = Literal["loc", "scale", "s", "mu", "n", "p", "low", "high"]


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
        # self.visibility: Literal["hide", "show"] = "show"
        self.data = []

    def get_sub_variables(self):
        return self.sub_variables

    def get_parameters(self, sub_variable: str):
        return self.sub_variables.get(sub_variable)

    def add_distribution(self):
        self.counter += 1
        new_params = ParameterTracker(DEFAULT_DISTRIBUTION[0])
        self.sub_variables.update({f"{self.variable}_{self.counter}": new_params})
        self.generate_data()

    def generate_data(self):
        np.random.seed(0)
        sub_variables = self.get_sub_variables()
        sub_variable_count = len(sub_variables)
        partition, rest = divmod(CONSTANTS.NR_DATA_POINTS, sub_variable_count)
        x = [partition for _ in range(sub_variable_count)]
        y = [1 if idx < rest else 0 for idx, _ in enumerate(range(sub_variable_count))]
        z = [a + b for a, b in zip(x,y)]
        data_container = []
        for parameters, nr_points in zip(sub_variables.values(), z):
            generator = parameters.generator
            value_dict = dict(map(lambda x: (x[0], x[1].value), parameters.get_ranges().items()))
            data = generator.rvs(**value_dict, size=nr_points)
            data_container.append(data)

        self.data = data_container

    def set_distribution(self, sub_var_name: str, params: ParameterTracker):
        self.sub_variables.update({sub_var_name: params})
        self.generate_data()

    def remove_sub_variable(self, sub_variable: str):
        assert self.sub_variables.get(sub_variable), "does not exist"
        if len(self.sub_variables.keys()) > 1:
            tmp = self.sub_variables.pop(sub_variable, None)
            self.generate_data()
            return tmp
        return None


class SliderTracker:
    variables: Dict[str, SubVariableTracker] = {}
    last_updated: str | None = None

    @staticmethod
    def get_variables():
        return SliderTracker.variables

    @staticmethod
    def get_sub_variables(variable: str):
        variables = SliderTracker.variables.get(variable)
        assert variables
        variables.generate_data()
        return variables

    @staticmethod
    def add_new_variable(variable: str):
        new_distr = SubVariableTracker(variable)
        new_distr.add_distribution()
        SliderTracker.variables.update({variable: new_distr})

    @staticmethod
    def remove_variable(variable: str):
        assert SliderTracker.variables.get(variable) is not None, "error"
        SliderTracker.variables.pop(variable)
