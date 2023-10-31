from dash import Dash, Input, Output, callback, html
from dash.dcc import Dropdown, Graph
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import scipy.stats as stats
import plotly.figure_factory as ff

norm = stats.norm.rvs(loc=0, scale=0.5, size=500)
log_norm = stats.lognorm.rvs(loc=0, scale=0.5, s=0.8, size=500)
laplace = stats.laplace.rvs(loc=0, scale=0.5, size=500)
uniform = stats.uniform.rvs(size=500)

dist_map = {
    "norm": norm,
    "log_norm": log_norm,
    "laplace": laplace,
    "uniform": uniform
}


fig_1 = ff.create_distplot([norm], ["norm"], show_hist=False, bin_size=0.2)
fig_2 = ff.create_distplot([log_norm], ["log_norm"], show_hist=False, bin_size=0.2)
fig_3 = ff.create_distplot([laplace], ["laplace"], show_hist=False, bin_size=0.2)
df = pd.DataFrame(
    np.array([norm, log_norm, laplace, uniform]).T,
    columns=["norm", "log_norm", "laplace", "uniform"]
)
fig_4 = ff.create_scatterplotmatrix(df, width=1200, height=1200, diag="histogram")

@callback(
    Output("graph4", "figure"),
    Input("dropdown", "value")
)
def scatter(values):
    if len(values) < 2:
        raise PreventUpdate
    choices = []
    for value in values:
        choices.append(dist_map.get(value))
    df_ = pd.DataFrame(
        np.array(choices).T,
        columns=values
    )
    fig_ = ff.create_scatterplotmatrix(df_, width=1200, height=1200, diag="histogram")

    return fig_


if __name__ == "__main__":
    app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
    app.layout = html.Div([
        html.H1("hello"),
        Graph(id="graph1", figure=fig_1),
        Graph(id="graph2", figure=fig_2),
        Graph(id="graph3", figure=fig_3),
        Graph(id="graph4", figure=fig_4),
        Dropdown(
            id="dropdown",
            options=["norm", "log_norm", "laplace", "uniform"],
            value=["norm", "log_norm"],
            multi=True
        )
    ])
    app.run(debug=True)

