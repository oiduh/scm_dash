from typing import Dict
from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.graph_objs import Layout
from plotly.graph_objs.layout._yaxis import YAxis

from distributions import Distributions
from components import MenuComponent


# globals (for now)
n: int = 300
distributions = Distributions()


# TODO: depending on structure -> 1 or 2 mechanism, 2 or 3 parameters
#   -> mechanism needs to be flexible
# TODO: intervention -> norm with loc=x, scale=0
def create_data(distr_x: str, distr_y: str, distr_z: str,
                kwargs_x: Dict[str, int | float],
                kwargs_y: Dict[str, int | float],
                kwargs_z: Dict[str, int | float],
                mechanism: str) -> pd.DataFrame:
    global n
    global distributions
    
    # noise generators
    distr_gen_x = distributions.get_generator(distr_x, kwargs_x)
    distr_gen_y = distributions.get_generator(distr_y, kwargs_y)
    distr_gen_z = distributions.get_generator(distr_z, kwargs_z)

    # noise values; if root cause -> noise=identity
    x = distr_gen_x.rvs(size=n)
    y = distr_gen_y.rvs(size=n)
    z = distr_gen_z.rvs(size=n)

    color = np.random.uniform(low=0, high=1, size=n)
    func = eval(f"lambda x, y: {mechanism}")
    color = ['True' if func(x_i, y_i) else 'False'
        for x_i, y_i in np.column_stack((x, y))]
    df = pd.DataFrame(np.array([x, y, color]).T, columns=['x', 'y', 'color'])
    df['x'] = df['x'].astype(np.float64)
    df['y'] = df['y'].astype(np.float64)
    df['color'] = df['color'].astype(str)
    return df


# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.Div(children='Simple scatter plot'),
    html.Hr(),
    html.Button('new', id='create-new-data', n_clicks=0),
    html.Div(id='container', children='click text'),
    html.Div(children=[
        html.Div(children=[MenuComponent(id='menu-component',
                                         distributions=distributions)],
                 style={'width': '49%', 'display': 'inline-block', 
                        'verticalAlign': 'top'}),
        html.Div(children=[dcc.Graph(figure={}, id='controls-and-graph')],
                 style={'width': '49%', 'display': 'inline-block'})
        ])
    ])

@callback(
        Output(component_id='distr-slider-x', component_property='children'),
        Output(component_id='distr-slider-y', component_property='children'),
        Output(component_id='distr-slider-z', component_property='children'),
        Input(component_id='distr-dropdown-x', component_property='value'),
        Input(component_id='distr-dropdown-y', component_property='value'),
        Input(component_id='distr-dropdown-z', component_property='value'),
        )
def update_distr_kwargs(distr_x, distr_y, distr_z):
    global distributions
    param_limits_x = distributions.get_values(distr_x)
    sliders_x = [html.Div([html.Label(f'{param_name}'),
                           dcc.Slider(min=param_range.min, max=param_range.max,
                                      # not providing the step -> 5 marks
                                      step=param_range.step,
                                      value=param_range.max,
                                      id={'type': 'distr_x_kwargs',
                                          'index': param_name})])
                 for param_name, param_range in param_limits_x.items()]
    param_limits_y = distributions.get_values(distr_y)
    sliders_y = [html.Div([html.Label(f'{param_name}'),
                           dcc.Slider(min=param_range.min, max=param_range.max,
                                      # not providing the step -> 5 marks
                                      step=param_range.step,
                                      value=param_range.max,
                                      id={'type': 'distr_y_kwargs',
                                          'index': param_name})])
                 for param_name, param_range in param_limits_y.items()]
    param_limits_z = distributions.get_values(distr_z)
    sliders_z = [html.Div([html.Label(f'{param_name}'),
                           dcc.Slider(min=param_range.min, max=param_range.max,
                                      # not providing the step -> 5 marks
                                      step=param_range.step, value=param_range.max,
                                      id={'type': 'distr_z_kwargs',
                                          'index': param_name})])
                 for param_name, param_range in param_limits_z.items()]
    return sliders_x, sliders_y, sliders_z

# Add controls to build the interaction
@callback(
        Output(component_id='controls-and-graph', component_property='figure'),
        Output(component_id='container', component_property='children'),
        Input(component_id='create-new-data', component_property='n_clicks'),
        Input(component_id='distr-dropdown-x', component_property='value'),
        Input(component_id='distr-slider-x', component_property='children'),
        Input(component_id='distr-dropdown-y', component_property='value'),
        Input(component_id='distr-slider-y', component_property='children'),
        Input(component_id='distr-dropdown-z', component_property='value'),
        Input(component_id='distr-slider-z', component_property='children'),
        )
def update_graph_and_table(
    n_clicks,
    distr_x, distr_x_kwargs,
    distr_y, distr_y_kwargs,
    distr_z, distr_z_kwargs
    ):
    # TODO: cleaner version with auto update?
    kwargs_x = dict()
    for x in distr_x_kwargs:
        for child in x['props']['children']:
            if child['type'].lower() == 'slider':
                key = child['props']['id']['index']
                value = child['props']['value'] 
                kwargs_x.update({key: value})
    kwargs_y = dict()
    for y in distr_y_kwargs:
        for child in y['props']['children']:
            if child['type'].lower() == 'slider':
                key = child['props']['id']['index']
                value = child['props']['value'] 
                kwargs_y.update({key: value})
    kwargs_z = dict()
    for z in distr_z_kwargs:
        for child in z['props']['children']:
            if child['type'].lower() == 'slider':
                key = child['props']['id']['index']
                value = child['props']['value'] 
                kwargs_z.update({key: value})

    mechanism = 'x > y'
    df = create_data(distr_x=distr_x, distr_y=distr_y, distr_z=distr_z,
                     kwargs_x=kwargs_x, kwargs_y=kwargs_y, kwargs_z=kwargs_z,
                     mechanism=mechanism)
    fig = px.scatter(df, x='x', y='y', color='color')
    fig.update_layout(autosize=False, height=800, width=1000)
    # TODO: add option -> equal scale and fill
    assert isinstance(fig.layout, Layout), "type checking"
    assert isinstance(fig.layout.yaxis, YAxis), "type checking"
    fig.layout.yaxis.scaleanchor = 'x'
    return fig, n_clicks

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
