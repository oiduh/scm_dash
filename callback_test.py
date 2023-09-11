from sys import exception
from dash import callback, Input, Output, Dash, html, State
from dash import dcc
from dash.dcc import Dropdown
import dash_bootstrap_components as dbc



GRAPH = {
    'a': ['b'],
    'b': ['c'],
    'c': []
}

class GraphBuilder:
    def __init__(self) -> None:
        global GRAPH
        self.graph = GRAPH

    def add_edge(self, new_edge):
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


app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.layout = html.Div([
    html.Div("graph builder"),
    html.Hr(),
    html.Div([
        dbc.Row([
            dbc.Col(GraphBuilderComponent(id='graph-builder-component')),
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
