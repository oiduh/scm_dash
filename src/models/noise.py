from scipy.stats import rv_continuous as RVCont, rv_discrete as RVDisc
import scipy.stats as stats
from dataclasses import dataclass, field
from models.mechanism import BaseMechanism


class CONSTANTS:
    NR_DATA_POINTS: int = 3000


Generator = RVCont | RVDisc


@dataclass
class Parameter():
    name: str
    min: float
    slider_min: float
    max: float
    slider_max: float
    current: float
    step: float

    def change_current(self, new_value: float):
        new_value = max(self.min, min(self.max, new_value))
        if new_value < self.slider_min:
            self.slider_min = new_value
        if new_value > self.slider_max:
            self.slider_max = new_value
        self.current = new_value

    def change_slider_min(self, new_value: float):
        self.slider_min = max(self.min, min(self.slider_max - self.step, new_value))

    def change_slider_max(self, new_value: float):
        self.slider_max = min(self.max, max(self.slider_min + self.step, new_value))


@dataclass
class Distribution:
    id: str
    name: str
    parameters: dict[str, Parameter]
    generator: Generator

    @staticmethod
    def parameter_options():
        options = [
            "normal", "lognorm", "uniform", "laplace", "poisson", "binom", "bernoulli", "randint"
        ]
        return options

    @classmethod
    def get_distribution(cls, id: str, name: str):
        match name:
            case "normal":
                loc = Parameter("loc", -10, -10, 10, 10, 0, 0.5)
                scale = Parameter("scale", 0, 0, 5, 5, 1, 0.1)
                return cls(id, name, {"loc": loc, "scale": scale}, stats.norm)
            case "lognorm":
                loc = Parameter("loc", -10, -10, 10, 10, 0, 0.5)
                scale = Parameter("scale", 0, 0, 5, 5, 1, 0.1)
                s = Parameter("s", 0, 0, 5, 5, 1, 0.1)
                return cls(id, name, {"loc": loc, "scale": scale, "s": s}, stats.lognorm)
            case "uniform":
                loc = Parameter("loc", -10, -10, 10, 10, 0, 0.5)
                scale = Parameter("scale", 0, 0, 5, 5, 1, 0.1)
                return cls(id, name, {"loc": loc, "scale": scale}, stats.uniform)
            case "laplace":
                loc = Parameter("loc", -10, -10, 10, 10, 0, 0.5)
                scale = Parameter("scale", 0, 0, 5, 5, 1, 0.1)
                return cls(id, name, {"loc": loc, "scale": scale}, stats.laplace)
            case "poisson":
                mu = Parameter("mu", 0, 0, 10, 10, 1, 0.1)
                return cls(id, name, {"mu": mu}, stats.poisson)
            case "binom":
                n = Parameter("n", 2, 2, 10, 10, 1, 1)
                p = Parameter("p", 0, 0, 1, 1, 0.5, 0.01)
                return cls(id, name, {"n": n, "p": p}, stats.binom)
            case "bernoulli":
                p = Parameter("p", 0, 0, 1, 1, 0.5, 0.01)
                return cls(id, name, {"p": p}, stats.bernoulli)
            case "randint":
                low = Parameter("low", 1, 1, 20, 20, 1, 1)
                high = Parameter("high", 2, 2, 21, 21, 5, 1)
                return cls(id, name, {"low": low, "high": high}, stats.randint)
            case _:
                assert False, "Unknown distribution"

    def change_distribution(self, name: str):
        new_distribution = Distribution.get_distribution(self.id, name)
        self.name = new_distribution.name
        self.parameters = new_distribution.parameters
        self.generator = new_distribution.generator

    def get_parameter_names(self):
        return list(self.parameters.keys())

    def get_parameter_by_name(self, name: str):
        assert name in self.get_parameter_names(), "parameter does not exist"
        return self.parameters[name]


@dataclass
class Data:
    id: str
    distributions: dict[str, Distribution | None] = field(
        default_factory=lambda: {str(nr): None for nr in range(10)}  # sub variables e.g. a_0, a_1
    )
    mechanism: BaseMechanism | None = None

    @classmethod
    def default_data(cls, id: str):
        data = cls(id)
        data.distributions['0'] = Distribution.get_distribution('0', "normal")
        return data

    def get_distributions(self):
        return [d for d in self.distributions.values() if d]

    def get_distribution_ids(self):
        return [d.id for d in self.get_distributions()]

    def get_distribution_by_id(self, id: str):
        assert id in self.get_distribution_ids(), "no distribution for this id"
        distribution = self.distributions.get(id)
        assert distribution, "distribution error"
        return distribution

    def get_free_id(self):
        free_ids = [d for d in self.distributions.keys() if not self.distributions.get(d)]
        return free_ids[0] if free_ids else None

    def add_distribution(self):
        free_id = self.get_free_id()
        assert free_id, "all ids have a distribution"
        self.distributions[free_id] = Distribution.get_distribution(free_id, "normal")

    def remove_distribution(self, to_remove: Distribution):
        assert to_remove.id in self.get_distribution_ids(), "id has no distribution"
        self.distributions[to_remove.id] = None

    def generate_data(self):
        distributions = self.get_distributions()
        partition, rest = divmod(CONSTANTS.NR_DATA_POINTS, len(distributions))
        x = [partition for _ in range(len(distributions))]
        y = [1 if idx < rest else 0 for idx, _ in enumerate(range(len(distributions)))]
        buckets = [a + b for a, b in zip(x, y)]
        # TODO: maybe dict to distinguish sub variable
        values = []
        for distribution, nr_points in zip(distributions, buckets):
            parameter_values = {v.name: v.current for v in distribution.parameters.values()}
            new_values = distribution.generator.rvs(**parameter_values, size=nr_points)
            values.append(new_values)

        return values

