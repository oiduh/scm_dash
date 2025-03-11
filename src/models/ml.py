from itertools import combinations
from sklearn.metrics import accuracy_score
from sklearn.linear_model import (
    LinearRegression,
    Ridge,
    Lasso,
)
from sklearn.model_selection import cross_val_score, train_test_split
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
from mvlearn.semi_supervised import (
    CTClassifier,
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
    SelfTrainingClassifier,
)
from sklearn.linear_model import (
    LogisticRegression,
    RidgeClassifier,
    SGDClassifier,
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


# TODO:should be merged with classification task once working
class SemiSupervisedClassification:
    def __init__(self) -> None:
        self.models = semi_supervised_classification_models

    # TODO: this needs adjustment since cv does not work; also include results for different percentages
    def evaluate_models(self, data: pd.DataFrame, sources: list[str], target: str) -> pd.DataFrame:
        source_matrix = data[sources].to_numpy()
        target_array = data[target].to_numpy()
        scores = []

        for model_type in self.models:
            model = model_type()
            model_scores = []
            for i in range(10):
                X_train, X_test, y_train, y_test = train_test_split(
                    source_matrix, target_array, test_size=.1, random_state=i
                )

                class_indices = np.unique(y_train)
                for class_index in class_indices:
                    indices = np.argwhere(y_train == class_index).reshape(1, -1)[0]
                    amount = int(np.floor(len(indices)*0.7))
                    unlabelled_indices = np.random.choice(indices, amount, False)
                    y_train[unlabelled_indices] = -1

                model.fit(X=X_train, y=y_train)
                model_scores.append(model.score(X_test, y_test))
            scores.append(
                [model.__class__.__name__, np.mean(model_scores) , np.std(model_scores)]
            )

        return (
            pd.DataFrame(scores, columns=["name", "mean", "std"])
            .sort_values(by=["mean"], ascending=False)
        )

self_training_classification_models = [
    DecisionTreeClassifier,
    GaussianNB,
    KNeighborsClassifier,
    LogisticRegression,
    RandomForestClassifier,
    GradientBoostingClassifier,
]

class SelfTrainingClassification:
    def __init__(self) -> None:
        self.models = self_training_classification_models


    def evaluate_models(self, data: pd.DataFrame, sources: list[str], target: str) -> pd.DataFrame:
        source_matrix = data[sources].to_numpy()
        target_array = data[target].to_numpy()
        scores = []

        for model_type in self.models:
            print(f"training model '{model_type}'")
            estimator = model_type()
            model = SelfTrainingClassifier(estimator)
            model_scores = []
            for i in range(10):
                X_train, X_test, y_train, y_test = train_test_split(
                    source_matrix, target_array, test_size=.1, random_state=i
                )

                class_indices = np.unique(y_train)
                for class_index in class_indices:
                    indices = np.argwhere(y_train == class_index).reshape(1, -1)[0]
                    amount = int(np.floor(len(indices)*0.7))
                    unlabelled_indices = np.random.choice(indices, amount, False)
                    y_train[unlabelled_indices] = -1

                model.fit(X=X_train, y=y_train)
                model_scores.append(model.score(X_test, y_test))
            scores.append(
                ["SelfTrainingClassifier " + estimator.__class__.__name__, np.mean(model_scores) , np.std(model_scores)]
            )

        return (
            pd.DataFrame(scores, columns=["name", "mean", "std"])
            .sort_values(by=["mean"], ascending=False)
        )

# FIXME:mvlearn has not been updated for a while, find another or implement from scratch
class CoTrainingClassification:
    def __init__(self) -> None:
        self.models = list(combinations(self_training_classification_models, 2))

    def evaluate_models(self, data: pd.DataFrame, sources: list[str], target: str) -> pd.DataFrame:
        source_matrix = data[sources].to_numpy()
        target_array = data[target].to_numpy()
        scores = []

        for estimators in self.models:
            estimator1 = estimators[0]()
            estimator2 = estimators[1]()
            print(f"training model '{estimator1.__class__.__name__}' and '{estimator2.__class__.__name__}'")
            model = CTClassifier(estimator1, estimator2)
            model_scores = []
            for i in range(10):
                X_train, X_test, y_train, y_test = train_test_split(
                    source_matrix, target_array, test_size=.1, random_state=i
                )
                y_train = y_train.astype(np.float64)
                y_test = y_test.astype(np.float64)

                class_indices = np.unique(y_train)
                for class_index in class_indices:
                    indices = np.argwhere(y_train == class_index).reshape(1, -1)[0]
                    amount = int(np.floor(len(indices)*0.7))
                    unlabelled_indices = np.random.choice(indices, amount, False)
                    y_train[unlabelled_indices] = np.nan

                model.fit([X_train, X_train], y_train)
                y_pred = model.predict([X_test, X_test])
                model_scores.append(accuracy_score(y_pred, y_test))
            scores.append([
                "CoTraining " + estimator1.__class__.__name__ + " " + estimator2.__class__.__name__,
                np.mean(model_scores),
                np.std(model_scores)
            ])

        return (
            pd.DataFrame(scores, columns=["name", "mean", "std"])
            .sort_values(by=["mean"], ascending=False)
        )

