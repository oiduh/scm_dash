# menu -> width 49%
# tabs -> 3x tab width 32% each
# tab 1 -> type of network graph: chain, fork, collider
# tab 2 -> distributions + sliders
# tab 3 -> mechanism
from dash.dcc import Tab, Tabs, Dropdown, Input, RadioItems
from dash import html
from dash.development._py_components_generation import Component
from typing import List, Optional
from distributions import Distributions

import numpy as np


class MenuComponent(html.Div):
    def __init__(self, children: Optional[List[Component]]=None, id=None, className=None,
                 contentEditable=None, style=None, title=None,*, distributions: Distributions):
        super().__init__(children, id, className, contentEditable, style, title)
        self.tab_container = Tabs(id='tab-container', value='mechanisms')
        self.tab_graph_type = Tab(label='Type', value='type')
        self.tab_distributions = Tab(label='Distributions', value='distributions')
        self.tab_mechanisms = Tab(label='Mechanisms', value='mechanisms')

        self.init_graph_type()
        self.init_distributions(distributions)
        self.init_mechanisms()

        self.tab_container.children = [self.tab_graph_type, self.tab_distributions, self.tab_mechanisms]
        self.children = [self.tab_container]

    def init_graph_type(self):
        # TODO: depending on graph -> different graph, mechanism etc.
        self.tab_graph_type.children = [
                html.Div(id='type-selection-container', children=[
                    RadioItems(id='select-graph-type', options=['chain', 'fork', 'collider'],
                               value='fork', inline=True)
                    ])
                ]

    def init_distributions(self, distributions: Distributions):
        component = DistributionsComponent(id='distr-comp', distributions=distributions)
        self.tab_distributions.children = component

    def init_mechanisms(self):
        x = np.array([1, 2, 6])
        y = np.array([4, 3, 2])
        op_string = 'lambda x, y: 2*(x + y) + 1'
        op = eval(op_string)
        res = op(x, y)

        self.tab_mechanisms.children = [
                html.Div(children=[
                    Input(id="input-array-1", type="text",  placeholder="1, 2, 3"),
                    Input(id="input-array-2", type="text",  placeholder="2, 3, 4"),
                    Input(id="input-mechanism", type="text",  placeholder="3 * x"),
                    html.Div(id='result', children=[]),
                    html.P(str(type(res))),
                    Dropdown(['x', 'y'], 'x'),
                    Dropdown(['x', 'y'], 'y'),
                    ])
                ]

class DistributionsComponent(html.Div):
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

# graph -> width 49%
# todo: more graphs e.g. tsne, histogram, corr mat
