from typing import Dict, List, Literal, NamedTuple
from scipy.stats import rv_continuous as RVCont, rv_discrete as RVDisc
import scipy.stats as stats
from scipy.stats._distn_infrastructure import rv_frozen as RVFrozen

KWARGS = Literal['loc', 'scale', 's', 'p', 'n']

class Range(NamedTuple):
    min: int | float
    max: int | float
    step: int | float

class DistributionsEntry(NamedTuple):
    distribution_class: RVCont | RVDisc
    values: Dict[KWARGS, Range]

_distribution_map: Dict[str, DistributionsEntry] = {
        'normal': DistributionsEntry(
            distribution_class=stats.norm,
            values={
                'loc': Range(min=-10.0, max=10.0, step=2.0),
                'scale': Range(min=0.0, max=3.0, step=0.3),
                }
            ),
        'lognorm': DistributionsEntry(
            distribution_class=stats.lognorm,
            values={
                'loc': Range(min=-10.0, max=10.0, step=2.0),
                'scale': Range(min=0.0, max=3.0, step=0.3),
                's': Range(min=0.0, max=2.0, step=0.2),
                }
            ),
        'bernoulli': DistributionsEntry(
            distribution_class=stats.bernoulli,
            values={
                'loc': Range(min=-10.0, max=10.0, step=2.0),
                'p': Range(min=0.0, max=1.0, step=0.1),
                }
            ),
        'binom': DistributionsEntry(
            distribution_class=stats.binom,
            values={
                'loc': Range(min=-10.0, max=10.0, step=2.0),
                'p': Range(min=0.0, max=1.0, step=0.1),
                'n': Range(min=1, max=11, step=1),
                }
            ),
        }

class Distributions:
    def __init__(self) -> None:
        global _distribution_map
        self.map = _distribution_map

    def get_class(self, key: str) -> RVCont | RVDisc:
        distribution = self.map.get(key, None)
        assert distribution is not None, "invalid key"
        return distribution.distribution_class

    def get_param_names(self, key: str) -> List[KWARGS]:
        distribution = self.map.get(key, None)
        assert distribution is not None, "invalid key"
        return list(distribution.values.keys())

    def get_values(self, key: KWARGS) -> Dict[KWARGS, Range]:
        distribution = self.map.get(key, None)
        assert distribution is not None, "invalid key"
        return distribution.values

    def filter_kwargs(self, key: str, sliders: Dict[str, int | float]) -> Dict[str, int | float]:
        values = {k: v for k, v in sliders.items() if k in self.get_param_names(key)}
        return values

   def get_generator(self, key: str, sliders: Dict[str, int | float]) -> RVFrozen:
        distribution_class = self.get_class(key)
        kwargs = self.filter_kwargs(key, sliders)
        distribution_generator = distribution_class(**kwargs)
        return distribution_generator



 
