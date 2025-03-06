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
        self.models = [model for model in regression_models]

    def evaluate_models(self, data: pd.DataFrame, sources: list[str], target: str) -> pd.DataFrame:
        source_matrix = data[sources].to_numpy()
        target_array = data[target].to_numpy()

        # scores = pd.DataFrame(columns=["name", "mean", "std"])
        scores = []
        for model_type in self.models:
            model = model_type()
            scores_ = cross_val_score(model, source_matrix, target_array, cv=10, n_jobs=6)
            scores.append([
                model.__class__.__name__, np.mean(scores_), np.std(scores_)
            ])

        return (
            pd.DataFrame(scores, columns=["name", "mean", "std"])
            .sort_values(by=["mean"], ascending=False)
        )

from sklearn.tree import (
    DecisionTreeClassifier,
)
from sklearn.naive_bayes import (
    GaussianNB,
)
from sklearn.neighbors import (
    KNeighborsClassifier,
)
from sklearn.semi_supervised import (
    LabelPropagation,
    LabelSpreading,
)
from sklearn.linear_model import (
    LogisticRegression,
    RidgeClassifier,
    SGDClassifier,
)
from sklearn.neural_network import (
    MLPClassifier,
)
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
)
from sklearn.svm import (
    SVC,
)

classification_models = [
    DecisionTreeClassifier,
    GaussianNB,
    KNeighborsClassifier,
    # LabelSpreading,
    # LabelPropagation,
    LogisticRegression,
    RidgeClassifier,
    SGDClassifier,
    MLPClassifier,
    RandomForestClassifier,
    GradientBoostingClassifier,
    SVC,
]

# TODO:for semi-supervised ml algos we need to think about how to choose unlabelled
# example data. just choosing at random might not work, since a class with little
# representation might get lost completely. for now lets choose a percentage e.g.
# 70% and make 70% of each class unlabelled. class distribution must not always be
# balanced. later it would make sense to run with various percentages.

# TODO: semi-supervised ml algos are not compatible with cross-validation-score
# since we have unlabelled data. we would need to implement a workaround, but with
# all other changes, that can be done separately. for classification we will exclude
# semi-supervised algorithms.

class Classification:
    def __init__(self) -> None:
        self.models = [model for model in classification_models]

    def evaluate_models(self, data: pd.DataFrame, sources: list[str], target: str) -> pd.DataFrame:
        source_matrix = data[sources].to_numpy()
        target_array = data[target].to_numpy()
        scores = []
        for model_type in self.models:
            model = model_type()
            print(f"running model {model.__class__.__name__}")
            scores_ = cross_val_score(model, source_matrix, target_array, cv=10, n_jobs=6)
            scores.append([
                model.__class__.__name__, np.mean(scores_), np.std(scores_)
            ])

        return (
            pd.DataFrame(scores, columns=["name", "mean", "std"])
            .sort_values(by=["mean"], ascending=False)
        )

semi_supervised_classification_models = [
    LabelPropagation,
    LabelSpreading,
]

class SemiSupervisedClassification:
    def __init__(self) -> None:
        self.models = semi_supervised_classification_models

    # TODO: this needs adjustment since cv does not work; also include results for different percentages
    def evaluate_models(self, data: pd.DataFrame, sources: list[str], target: str) -> pd.DataFrame:
        pass
        #
        # np.random.seed(0)
        #
        # print(target_array)
        # class_indices = np.unique(target_array)
        # new_target = np.copy(target_array)
        # for class_index in class_indices:
        #     indices = np.argwhere(target_array == class_index)
        #     amount = np.floor(len(indices)*0.7)
        #     unlabelled_indices = np.random.choice(indices, amount, False)
        #     new_target[unlabelled_indices] = -1
        #
