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


# TODO: depending on structure -> 1 or 2 mechanism, 2 or 3 parameters -> mechanism needs to be flexible
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

    # TODO: depending on chosen structure -> apply mechanism and noise
    # 1) chain: x -> y=f(x, y_n) -> z=g(y, z_n)=g(f(x, x_n), y_n)
    # 2) fork: x=f(y, x_n) <- y -> z=g(y, z_n)
    # 3) collider: x -> y=f(x, z, y_n) <- z
    # how to properly distinct between continuous and discrete output?
    # type of output should be independent of noise -> output can be continuous while noise is binary
    # and vice versa; idea: detect whether output has more than 10 int values or something


    # use this to distinguish between graph types, when implemented
    graph_type = "collider"
    match graph_type:
        case "colider":
            # x=x_n -> y=f(x, z, y_n) <- z=z_n
            func = eval(f"lambda x, y, z: {mechanism}")
            cause1 = x
            cause2 = z
            result_noise = y
            result = func(cause1, cause2, result_noise)

            pass
        case "fork":
            # x=f(y, x_n) <- y=y_n -> z=g(y, z_n)
            func1 = eval(f"lambda x, y: {mechanism}")
            func2 = eval(f"lambda y, z: {mechanism}")
            cause1 = y
            noise1 = x
            noise2 = z
            result1 = func1(cause1, noise1, noise2)
            pass
        case "chain":
            # x=x_n -> y=f(x, y_n)=f(x_n, y_n) -> z=g(y, z_n)=g(f(x_n, y_n), z_n)
            func1 = eval(f"lambda x, y: {mechanism}")
            res_x = func1(x, y)
            # eval func1
            func2 = eval(f"lambda z: {mechanism}")
            pass
        case _:
            pass

    color = np.random.uniform(low=0, high=1, size=n)
    func = eval(f"lambda x, y: {mechanism}")
    color = ['True' if func(x_i, y_i) else 'False' for x_i, y_i in np.column_stack((x, y))]
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
        html.Div(children=[MenuComponent(id='menu-component', distributions=distributions)],
                 style={'width': '49%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        html.Div(children=[dcc.Graph(figure={}, id='controls-and-graph')],
                 style={'width': '49%', 'display': 'inline-block'})
        ])
    ])

@callback(
        Output(component_id='result', component_property='children'),
        Input(component_id='input-array-1', component_property='value'),
        Input(component_id='input-array-2', component_property='value'),
        Input(component_id='input-mechanism', component_property='value'),
        )
def test_mechansim(arr_1: str, arr_2: str, mech: str):
    if arr_1 and arr_2:
        arr_1_int = np.array([int(x) for x in arr_1.replace(' ', '').split(',')])
        print(f"{arr_1_int=}")
        arr_2_int = np.array([int(x) for x in arr_2.replace(' ', '').split(',')])
        print(f"{arr_2_int=}")
        if len(arr_1_int) != len(arr_2_int):
            return ['len error']
        try:
            func_str = f"lambda x, y: {mech}"
            print(f"{func_str=}")
            func = eval(func_str)
            res = func(arr_1_int, arr_2_int)
            return [str(res)]
        except Exception:
            return ['mech error']

    return ['error']

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
                                      step=param_range.step, value=param_range.max,
                                      id={'type': 'distr_x_kwargs', 'index': param_name})])
                 for param_name, param_range in param_limits_x.items()]
    param_limits_y = distributions.get_values(distr_y)
    sliders_y = [html.Div([html.Label(f'{param_name}'),
                           dcc.Slider(min=param_range.min, max=param_range.max,
                                      # not providing the step -> 5 marks
                                      step=param_range.step, value=param_range.max,
                                      id={'type': 'distr_y_kwargs', 'index': param_name})])
                 for param_name, param_range in param_limits_y.items()]
    param_limits_z = distributions.get_values(distr_z)
    sliders_z = [html.Div([html.Label(f'{param_name}'),
                           dcc.Slider(min=param_range.min, max=param_range.max,
                                      # not providing the step -> 5 marks
                                      step=param_range.step, value=param_range.max,
                                      id={'type': 'distr_z_kwargs', 'index': param_name})])
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
        Input(component_id='input-mechanism', component_property='value'),
        )
def update_graph_and_table(n_clicks, distr_x, distr_x_kwargs, distr_y, distr_y_kwargs, mechanism):
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

    df = create_data(distr_x=distr_x, distr_y=distr_y, kwargs_x=kwargs_x, kwargs_y=kwargs_y,
                     mechanism=mechanism)
    fig = px.scatter(df, x='x', y='y', color='color')
    fig.update_layout(autosize=False, height=800, width=1000)
    # TODO: add option -> equal scale and fill
    assert isinstance(fig.layout, Layout), "type checking"
    assert isinstance(fig.layout.yaxis, YAxis), "type checking"
    fig.layout.yaxis.scaleanchor = 'x'
    # data = df.to_dict('records')
    # return fig, data, n_clicks
    return fig, n_clicks

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
