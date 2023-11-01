from dash import Dash, Input, Output, callback, callback_context, html, State
from dash.dcc import Dropdown, Graph, Checklist
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
    Output("distr-checklist", "value"),
    Output("all-checklist", "value"),
    Output("graph4", "figure"),
    Input("distr-checklist", "value"),
    Input("all-checklist", "value"),
    State("graph4", "figure")
)
def checklist(distrs, all, fig):
    ctx = callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id == "distr-checklist":
        all = ["All"] if set(distrs) == set(dist_map.keys()) else []
    else:
        distrs = list(dist_map.keys()) if all else []

    print(set(distrs).intersection(set(dist_map.keys())))
    selected = list(set(distrs).intersection(set(dist_map.keys())))
    if len(selected) == 1:
        [value] = selected
        fig = ff.create_distplot(
            hist_data=[dist_map.get(value)],
            group_labels=[value],
            show_rug=False,
            bin_size=0.2
        )
    elif len(selected) > 1:
        choices = []
        for value in selected:
            choices.append(dist_map.get(value))
        df_ = pd.DataFrame(
            np.array(choices).T,
            columns=selected
        )
        fig = ff.create_scatterplotmatrix(
            df=df_,
            diag="histogram",
            width=1200,
            height=1200
        )

    return distrs, all, fig


if __name__ == "__main__":
    app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
    app.layout = html.Div([
        html.H1("hello"),
        Graph(id="graph1", figure=fig_1),
        Graph(id="graph2", figure=fig_2),
        Graph(id="graph3", figure=fig_3),
        Graph(id="graph4", figure=fig_4),
        Checklist(["All"], ["All"],  id="all-checklist", inline=True),
        Checklist(list(dist_map.keys()), [], id="distr-checklist", inline=True),

    ])
    app.run(debug=True)

