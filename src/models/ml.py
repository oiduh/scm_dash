from sklearn.linear_model import (
    LinearRegression,
    Ridge,
    Lasso,
)
from sklearn.model_selection import cross_val_score
from sklearn.tree import (
    DecisionTreeRegressor,
)
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    AdaBoostRegressor,
)
from sklearn.neighbors import (
    KNeighborsRegressor,
)
from sklearn.svm import (
    SVR,
)
from sklearn.gaussian_process import (
    GaussianProcessRegressor,
)
import pandas as pd
import numpy as np

# TODO: make a generic model if possible
# group multiple algos and execute them with proper parameters
# start simple e.g. one run with base params
# add complexity e.g. cross-validation, multiple runs(?)

regression_models = [
    LinearRegression,
    Ridge,
    Lasso,
    DecisionTreeRegressor,
    RandomForestRegressor,
    GradientBoostingRegressor,
    AdaBoostRegressor,
    KNeighborsRegressor,
    SVR,
    GaussianProcessRegressor,
]


class Regression:
    def __init__(self) -> None:
        self.models = {
            model.__class__.__name__: model for model in regression_models
        }

    def evaluate_models(self, data: pd.DataFrame, sources: list[str], target: str) -> pd.DataFrame:
        source_matrix = data[sources].to_numpy()
        target_array = data[target].to_numpy()

        scores = pd.DataFrame(columns=["name", "mean", "std"])
        for model_type in self.models.values():
            model = model_type()
            scores_ = cross_val_score(model, source_matrix, target_array, cv=10)
            scores = scores.append({
                "name": model.__class__.__name__, "mean": np.mean(scores_), "std": np.std(scores_)
            }, ignore_index=True)
        return scores



