from sys import exception
from typing import Tuple
from dash import callback, Input, Output, Dash, html, State
from dash import dcc
from dash.dcc import Dropdown
import dash_bootstrap_components as dbc
from pandas.core.internals.concat import cp



GRAPH = {
    'a': ['b'],
    'b': ['c'],
    'c': []
}

INDEX = {
    '0': 'a',
    '1': 'b'
}

class GraphBuilder:
    current_id = 'b'

    def __init__(self) -> None:
        global GRAPH, INDEX
        self.graph = GRAPH
        self.index = INDEX

    def add_edge(self, new_edge: Tuple[str, str]):
        cause, effect = new_edge
        graph_copy = self.graph.copy()
        if (g:=graph_copy.get(cause, None)) is not None:
            g.append(effect)
        else:
            graph_copy.update({cause: [effect]})

        if (g:=graph_copy.get(effect, None)) is None:
            graph_copy.update({effect: []})

        if GraphBuilder.is_cyclic(graph_copy):
            raise Exception("cannot add this edge -> no cycles allowed")
        else:
            self.graph = graph_copy
            next_index = list(self.index.keys())[-1]
            next_index = int(next_index) + 1
            self.index[str(next_index)] = cause

    @staticmethod
    def is_cyclic_util(node, visited, rec_stack, graph):
        visited[node] = True
        rec_stack[node] = True
        for neighbor in graph[node]:
            if not visited[neighbor]:
                if GraphBuilder.is_cyclic_util(neighbor, visited, rec_stack, graph):
                    return True
            elif rec_stack[neighbor]:
                return True
        rec_stack[node] = False
        return False

    @staticmethod
    def is_cyclic(new_graph):
        visited = {k: False for k in new_graph.keys()}
        rec_stack = {k: False for k in new_graph.keys()}
        for node in new_graph.keys():
            if not visited[node]:
                if GraphBuilder.is_cyclic_util(node, visited, rec_stack, new_graph):
                    return True
        return False

    def new_node(self, index):
        if GraphBuilder.current_id[-1] == 'z':
            GraphBuilder.current_id += 'a'
        else:
            cpy = GraphBuilder.current_id
            last = cpy[-1]
            new = cpy[:-1] + chr(ord(last) + 1)
            GraphBuilder.current_id = new
        self.index[index] = GraphBuilder.current_id
            

graph_builder = GraphBuilder()

class GraphBuilderComponent(html.Div):
    def __init__(self, id, style=None):
        global graph_builder
        super().__init__(id=id, style=style)
        self.graph_builder = graph_builder
        self.children = []
        self.style = {
            'border': '2px black solid',
            'margin': '2px'
        }
        for cause, effects in self.graph_builder.graph.items():
            variable_component = html.Div(id=f"{cause}", style={
                'border': '2px black solid',
                'margin': '2px'
            })
            variable_component.children = [
                html.P(f"variable: {cause}"),
                html.P(f"effects: {', '.join(effects) if effects else 'None'}")
            ]
            self.children.append(variable_component)

    def add_node(self, node):
        pass

    def add_edge(self, source, target):
        pass

    def remove_node(self, node):
        pass

    def remove_edge(self, source, target):
        pass


app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.layout = html.Div([
    html.Div("graph builder"),
    html.Hr(),
    html.Div([
        dbc.Row([
            dbc.Col(
                dbc.Row([
                    GraphBuilderComponent(id='graph-builder-component'),
                    html.Label("Add Node"),
                    html.Button(id='add-node-button', children="Add Node",
                                n_clicks=2)
                ])
            ),
            dbc.Col(html.Div(children=['some text']))
        ]),
        dbc.Row([
            dbc.Col(html.Div('123')),
            dbc.Col(html.Div('456')),
            dbc.Col(html.Div('789'))
        ]),
        dbc.Row([
            dbc.Col(html.Div('123')),
            dbc.Col(html.Div('456')),
            dbc.Col(html.Div('789')),
            dbc.Col(html.Div('123')),
            dbc.Col(html.Div('456')),
            dbc.Col(html.Div('789'))
        ])
    ])
])

@callback(
    Output('graph-builder-component', 'children'),
    Input('add-node-button', 'n_clicks'),
    State('graph-builder-component', 'children')
)
def add_new_node(index, current_state):
    global graph_builder
    graph_builder.new_node(str(index))
    print(graph_builder.current_id)
    print(graph_builder.index)
    return current_state

# @callback(
#     Output(component_id='first', component_property='children'),
#     Output(component_id='second', component_property='children'),
#     Input(component_id='confirm-button', component_property='n_clicks'),
#     State(component_id='first-state', component_property='value'),
#     State(component_id='second-state', component_property='value')
# )
# def state_test(_, first_input, second_input):
#     return first_input, second_input


if __name__ == '__main__':
    app.run(debug=True)
