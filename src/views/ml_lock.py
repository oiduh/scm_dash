from dash import html, dcc
import dash_bootstrap_components as dbc
from sklearn.linear_model import (
    LinearRegression,
    Ridge,
    Lasso,
    SGDRegressor,
    BayesianRidge,
)
from sklearn.mixture import (
    BayesianGaussianMixture,
    GaussianMixture,
)
from sklearn.svm import (
    SVR,
    NuSVR,
)
from sklearn.neighbors import (
    KNeighborsRegressor,
    RadiusNeighborsRegressor,
)
from sklearn.gaussian_process import (
    GaussianProcessRegressor,
)
from sklearn.model_selection import cross_val_score
from models.graph import graph
import numpy as np

class MLLockBuilder(html.Div):
    is_locked: bool = False
    def __init__(self):
        super().__init__(id="ml-lock-builder")
        buttons = []
        if MLLockBuilder.is_locked:
            if len(graph.data_sets) > 0 and graph.data is not None:
                print(graph.data_sets[0])
                print(graph.data)
                source_ = graph.data_sets[0]["s"]
                target_ = graph.data_sets[0]["t"]
                source = graph.data[source_].to_numpy()
                target = graph.data[target_].to_numpy()
                models = [
                    LinearRegression,
                    Ridge,
                    Lasso,
                    SGDRegressor,
                    BayesianRidge,
                    BayesianGaussianMixture,
                    GaussianMixture,
                    GaussianProcessRegressor,
                    SVR,
                    NuSVR,
                    KNeighborsRegressor,
                    RadiusNeighborsRegressor,
                ]
                for model in models:
                    model_ = model()
                    scores = cross_val_score(model_, source, target, cv=10)
                    print(f"{model_.__class__.__name__} results: {np.mean(scores)=}, {np.std(scores)=}")
            buttons.extend([
                html.Button("Unlock", id="ml-lock-button"),
            ])
        else:
            buttons.append(
                html.Button("Lock", id="ml-lock-button"),
            )
        self.children = [
            dbc.Row(
                dbc.Col(
                    buttons,
                    width="auto"
                ),
                justify="center"
            )
        ]

class MLLockViewer(html.Div):
    def __init__(self):
        # TODO: add progress bars for each data set and each algo in training
        super().__init__(id="ml-lock-viewer")
        self.children = []
