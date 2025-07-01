from dataclasses import dataclass, field
import string
from typing import Any, Self

import numpy as np
import scipy.stats as stats
from scipy.stats import rv_continuous as RVCont
from scipy.stats import rv_discrete as RVDisc


class GLOBAL_VARIABLES:
    NR_DATA_POINTS: int = 1000
    MIN_DATA_POINTS: int = 300
    MAX_DATA_POINTS: int = 3000
    SEED: int = 0  # TODO: make it configurable


Generator = RVCont | RVDisc


@dataclass(kw_only=True)
class Parameter:
    name: str
    real_name: str
    min: float
    slider_min: float
    max: float
    slider_max: float
    current: float
    step: float

    def change_current(self, new_value: float) -> None:
        new_value = max(self.min, min(self.max, new_value))
        self.slider_min = min(new_value, self.slider_min)
        self.slider_max = max(new_value, self.slider_max)
        self.current = new_value

    # TODO: not used
    def change_slider_min(self, new_value: float) -> None:
        self.slider_min = max(self.min, min(self.slider_max - self.step, new_value))

    # TODO: not used
    def change_slider_max(self, new_value: float) -> None:
        self.slider_max = min(self.max, max(self.slider_min + self.step, new_value))


@dataclass
class Distribution:
    id_: str
    name: str
    # dependant on the type, 'parameters' & 'generator' do different things
    parameters: dict[str, Parameter]
    generator: Generator

    @staticmethod
    def parameter_options() -> list[str]:
        options = [
            "normal",
            "lognorm",
            "uniform",
            "laplace",
            # "poisson",
            # "binom",
            # "bernoulli",
            "randint",
        ]
        return options

    @classmethod
    def get_distribution(cls, id: str, name: str) -> Self | None:
        match name:
            case "normal":
                # mean (mu)
                loc = Parameter(
                    name="loc",
                    real_name="mean",
                    min=-10,
                    slider_min=-10,
                    max=10,
                    slider_max=10,
                    current=0,
                    step=0.5,
                )
                # variance (phi)
                scale = Parameter(
                    name="scale",
                    real_name="variance",
                    min=0.1,
                    slider_min=0.1,
                    max=5,
                    slider_max=5,
                    current=1,
                    step=0.1,
                )
                return cls(id, name, {"loc": loc, "scale": scale}, stats.norm)
            case "lognorm":
                # mean (mu)
                loc = Parameter(
                    name="loc",
                    real_name="mean",
                    min=-10,
                    slider_min=-10,
                    max=10,
                    slider_max=10,
                    current=0,
                    step=0.5,
                )
                # variance (phi)
                scale = Parameter(
                    name="scale",
                    real_name="variance",
                    min=0,
                    slider_min=0,
                    max=5,
                    slider_max=5,
                    current=1,
                    step=0.1,
                )
                # shape (s)
                s = Parameter(
                    name="s",
                    real_name="shape",
                    min=0.1,
                    slider_min=0.1,
                    max=1.0,
                    slider_max=1.0,
                    current=1,
                    step=0.1,
                )
                return cls(
                    id, name, {"loc": loc, "scale": scale, "s": s}, stats.lognorm
                )
            case "uniform":
                # start (loc)
                loc = Parameter(
                    name="loc",
                    real_name="start",
                    min=-10,
                    slider_min=-10,
                    max=10,
                    slider_max=10,
                    current=0,
                    step=0.5,
                )
                # length (scale)
                scale = Parameter(
                    name="scale",
                    real_name="length",
                    min=0,
                    slider_min=0,
                    max=5,
                    slider_max=5,
                    current=1,
                    step=0.1,
                )
                # generates uniformely distriributed data in range [a, a + b]
                return cls(id, name, {"loc": loc, "scale": scale}, stats.uniform)
            case "laplace":
                # locations
                loc = Parameter(
                    name="loc",
                    real_name="location",
                    min=-10,
                    slider_min=-10,
                    max=10,
                    slider_max=10,
                    current=0,
                    step=0.5,
                )
                # scale
                scale = Parameter(
                    name="scale",
                    real_name="scale",
                    min=0,
                    slider_min=0,
                    max=5,
                    slider_max=5,
                    current=1,
                    step=0.1,
                )
                # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.laplace.html
                return cls(id, name, {"loc": loc, "scale": scale}, stats.laplace)
            case "poisson":
                # mu
                mu = Parameter(
                    name="mu",
                    real_name="mu",
                    min=0,
                    slider_min=0,
                    max=10,
                    slider_max=10,
                    current=1,
                    step=0.1,
                )
                # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.poisson.html
                return cls(id, name, {"mu": mu}, stats.poisson)
            case "binom":
                # n -> determines max int value for range k=[0, n]
                n = Parameter(
                    name="n",
                    real_name="n",
                    min=2,
                    slider_min=2,
                    max=10,
                    slider_max=10,
                    current=1,
                    step=1,
                )
                # p -> probability [0, 1]
                p = Parameter(
                    name="p",
                    real_name="p",
                    min=0,
                    slider_min=0,
                    max=1,
                    slider_max=1,
                    current=0.5,
                    step=0.01,
                )
                # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binom.html
                return cls(id, name, {"n": n, "p": p}, stats.binom)
            case "bernoulli":
                # p -> probability [0, 1]
                p = Parameter(
                    name="p",
                    real_name="p",
                    min=0,
                    slider_min=0,
                    max=1,
                    slider_max=1,
                    current=0.5,
                    step=0.01,
                )
                # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bernoulli.html
                return cls(id, name, {"p": p}, stats.bernoulli)
            case "randint":
                low = Parameter(
                    name="low",
                    real_name="low",
                    min=1,
                    slider_min=1,
                    max=20,
                    slider_max=20,
                    current=1,
                    step=1,
                )
                high = Parameter(
                    name="high",
                    real_name="high",
                    min=2,
                    slider_min=2,
                    max=21,
                    slider_max=21,
                    current=5,
                    step=1,
                )
                # [low, high - 1]
                return cls(id, name, {"low": low, "high": high}, stats.randint)
            case _:
                return None

    def change_distribution(self, name: str) -> None:
        new_distribution = Distribution.get_distribution(self.id_, name)
        assert new_distribution is not None

        self.id_ = new_distribution.id_
        self.name = new_distribution.name
        self.parameters = new_distribution.parameters
        self.generator = new_distribution.generator

    def get_parameter_names(self) -> list[str]:
        return list(self.parameters.keys())

    def get_parameter_by_name(self, name: str) -> Parameter | None:
        if name not in self.get_parameter_names():
            return None
        return self.parameters.get(name)

    @classmethod
    def parse_from_dict(cls, id_: str, distribution_dict: dict) -> Self:
        assert (name := distribution_dict.get("name")) is not None and name in cls.parameter_options(), (
            "invalid distribution name"
        )
        assert (params := distribution_dict.get("params")) is not None and isinstance(params, dict), (
            "invalid distribution params"
        )

        new_distribution = Distribution.get_distribution(id_, name)
        assert new_distribution is not None
        for id_, current in params.items():
            assert isinstance(current, float | int), "current not a float"
            default_param = new_distribution.parameters.get(id_)
            assert default_param is not None
            assert default_param.min <= current <= default_param.max, "current invalid range"
            new_distribution.parameters[id_].change_current(current)
        return cls(
            id_=new_distribution.id_,
            name=new_distribution.name,
            parameters=new_distribution.parameters,
            generator=new_distribution.generator
        )


@dataclass
class Noise:
    sub_distributions: dict[str, Distribution | None] = field(
        default_factory=lambda: {
            str(nr): None for nr in range(10)
        }  # sub variables e.g. a_0, a_1
    )
    data: dict[str, np.ndarray] = field(default_factory=dict)

    @classmethod
    def default_noise(cls) -> Self:
        noise = cls()
        noise.sub_distributions["0"] = Distribution.get_distribution("0", "uniform")
        return noise

    def get_distributions(self) -> list[Distribution]:
        return [d for d in self.sub_distributions.values() if d is not None]

    def get_distribution_ids(self) -> list[str]:
        return [d.id_ for d in self.get_distributions()]

    def get_distribution_by_id(self, id_: str) -> Distribution | None:
        if id_ not in self.get_distribution_ids():
            return None
        return self.sub_distributions.get(id_)

    def get_free_id(self) -> str | None:
        free_ids = [
            d for d in self.sub_distributions.keys()
            if self.sub_distributions.get(d) is None
        ]
        return free_ids[0] if len(free_ids) > 0 else None

    def add_distribution(self) -> str:
        """
        Exception:
            cannot add another sub distribution
        """
        free_id = self.get_free_id()
        if free_id is None:
            raise Exception("Cannot add another distribution")
        self.sub_distributions[free_id] = Distribution.get_distribution(
            free_id, "normal"
        )
        return free_id

    def remove_distribution(self, to_remove: Distribution) -> None:
        """
        Exception:
            cannot remove this sub distribution
        """
        if to_remove.id_ not in self.get_distribution_ids():
            raise Exception("Cannot remove this distribution")
        self.sub_distributions[to_remove.id_] = None

    def generate_data(self) -> dict[str, np.ndarray]:
        # TODO: potentially think about using a custom seed
        np.random.seed(42)
        distributions = self.get_distributions()
        partition, rest = divmod(GLOBAL_VARIABLES.NR_DATA_POINTS, len(distributions))
        x = [partition for _ in range(len(distributions))]
        y = [1 if idx < rest else 0 for idx, _ in enumerate(range(len(distributions)))]
        buckets = [a + b for a, b in zip(x, y)]
        values: dict[str, np.ndarray] = {}
        for distribution, nr_points in zip(distributions, buckets):
            parameter_values = {
                v.name: v.current for v in distribution.parameters.values()
            }
            # TODO: setting for seed via UI?
            # np.random.seed(0)
            new_values: np.ndarray = distribution.generator.rvs(**parameter_values, size=nr_points)  # type: ignore
            values[distribution.id_] = new_values
        self.data = values
        return values

    @classmethod
    def parse_from_dict(cls, noise_data: dict[str, Any]) -> Self:
        new_noise = cls()

        assert all(isinstance(id_, str) and len(id_) == 1 and id_ in string.digits for id_ in noise_data.keys()), (
            "invalid noise id"
        )
        assert all(isinstance(d, dict) for d in noise_data.values()), (
            "invalid noise dict"
        )

        for id_, sub_distr in noise_data.items():
            new_sub_distribution = Distribution.parse_from_dict(id_, sub_distr)
            new_noise.sub_distributions[id_] = new_sub_distribution

        return new_noise
