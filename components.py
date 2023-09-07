from dash.dcc import Tab, Tabs, Dropdown, Input as InputText
from dash import dcc, html, callback, Output, Input, ctx
from dash.development._py_components_generation import Component
from typing import Dict, List, Optional
from distributions import Distributions
from graph_test import AdjecencyList
import dash_cytoscape as cyto

import numpy as np

GRAPH_TYPES: List[str] = ['chain', 'fork', 'collider', 'custom']


class MenuComponent(html.Div):
    """
    Main componenent acting as tab container for other tabs:
        * graph type e.g. nodes and edges
        * distributions e.g. noise for each variable
        * mechanism e.g. x->y means y=f(x)
    """
    def __init__(self, children: Optional[List[Component]]=None, id=None,
                 className=None, contentEditable=None, style=None, title=None,
                 *, distributions: Distributions):
        super().__init__(children, id, className, contentEditable, style, title)
        self.tab_container = Tabs(id='tab-container', value='type')
        self.tab_graph_type = Tab(label='Type', value='type')
        self.tab_distributions = Tab(label='Distributions', value='distributions')
        self.tab_mechanisms = Tab(label='Mechanisms', value='mechanisms')

        self.init_graph_type()
        self.init_distributions(distributions)
        self.init_mechanisms()

        self.tab_container.children = [
            self.tab_graph_type,self.tab_distributions, self.tab_mechanisms
        ]
        self.children = [self.tab_container, html.Div(id='test', children='nothing yet')]

    def init_graph_type(self):
        component = GraphComponent(id='graph-component')
        self.tab_graph_type.children = component

    def init_distributions(self, distributions: Distributions):
        component = DistributionComponent(id='distr-comp', distributions=distributions)
        self.tab_distributions.children = component

    def init_mechanisms(self):
        component = MechanismComponent(id='mechanism-component')
        self.tab_mechanisms.children = component

        


class GraphComponent(html.Div):
    # TODO: could also be arbitrary with adj mat
    def __init__(self, id, children=None, title=None):
        # default choices

        super().__init__(children, id, title)
        self.children = [
            html.Div(id='graph-type-selection', children=[
                Dropdown(id='select-graph-type',
                         options=GRAPH_TYPES, value=GRAPH_TYPES[0]),
                html.Div(id='show-selected-graph', children=None),
                html.Button('Confirm', id='confirm-graph-type', n_clicks=0)
            ])
        ]

    @staticmethod
    @callback(
        Output(component_id='show-selected-graph', component_property='children'),
        Input(component_id='select-graph-type', component_property='value')
    )
    def callback_graph_selection(selected_graph_type: str):
        chain = AdjecencyList(
            [('x', 'y'), ('y', 'z')]
        )
        fork = AdjecencyList([('y', 'x'), ('y', 'z')])
        collider = AdjecencyList([('x', 'y'), ('z', 'y')])

        # TODO: add custom choice -> input=adj_list

        graphs: Dict[str, cyto.Cytoscape] = dict()
        for name, adj_list in zip(
            ['chain', 'fork', 'collider'],[chain, fork, collider]
        ):
            elements = adj_list.to_cyto()
            style = {
                'width': '400px', 'height': '500px',
                'border': '2px black solid',
                'margin': '2px'
            }
            layout = {'name': 'grid'}
            stylesheet = [
                {
                    'selector': 'edge',
                    'style': {
                        'curve-style': 'bezier',
                        'source-arrow-shape': 'triangle'
                    }
                },
                {
                    'selector': 'node',
                    'style': {
                        'label': 'data(id)',
                    }
                }
            ]

            graphs.update({name: cyto.Cytoscape(
                elements=elements,
                style=style,
                layout=layout,
                stylesheet=stylesheet
            )})

        match selected_graph_type.lower():
            case 'chain' | 'fork' | 'collider':
                selected_graph = graphs[selected_graph_type]
            case 'custom':
                selected_graph = html.Div("TODO: ...")
            case _:
                assert False, 'unknown type'

        return selected_graph


class DistributionComponent(html.Div):
    def __init__(self, id, children=[], title=None, *, distributions: Distributions):
        assert distributions is not None, "error"
        super().__init__(children, id, title)
        variables = ['x', 'y', 'z']
        style = {'width': '32%', 'display': 'inline-block', 'verticalAlign': 'top',
                      'border': '2px black solid', 'margin': '2px'}
        dropdown_template = lambda var_name: html.Div([
            html.P(var_name),
            Dropdown([name for name in distributions.map], 'normal',
                     id=f'distr-dropdown-{var_name}'),
            html.Hr(),
            html.Div(id=f'distr-slider-{var_name}', children=[])], style=style)
        dropdowns = [dropdown_template(var) for var in variables]
        self.children = dropdowns

class MechanismComponent(html.Div):
    def __init__(self, id, children=None, title=None):
        global GRAPH_TYPES
        super().__init__(children, id, title)
        x = np.array([1, 2, 6])
        y = np.array([4, 3, 2])
        op_string = 'lambda x, y: 2*(x + y) + 1'
        op = eval(op_string)
        res = op(x, y)

        self.children = [
            html.P("TODO: ...")
        ]


# CALLBACKS

@callback(
    Output(component_id='mechanism-component', component_property='children'),
    Input(component_id='confirm-graph-type', component_property='n_clicks'),
    Input(component_id='select-graph-type', component_property='value'),
)
def confirm_graph_type(_, graph_type):
    # TODO: 
    #       - depending on choice -> mechanism
    #       - use button to confirm choice
    #       - if dropdown value changed -> reset all
    if ctx.triggered_id != 'confirm-graph-type':
        return 'nothing selected'
    
    style = {
        'width': '400px', 'height': '500px',
        'border': '2px black solid',
        'margin': '2px'
    }
    list_of_elements = []
    list_of_elements.extend([
        html.P(f"selected graph type: {graph_type}"),
        html.Div(id='x_arg', children=[
            html.P('x_arg'),
            InputText(id='x_arg_input')
        ], style=style),
        html.Div(id='y_arg', children=[
            html.P('y_arg'),
            InputText(id='y_arg_input')
        ], style=style),
        html.Div(id='z_arg', children=[
            html.P('z_arg'),
            InputText(id='z_arg_input')
        ], style=style),
    ])

    return list_of_elements

