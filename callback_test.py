from typing import Tuple
from dash import ALL, MATCH, callback, Input, Output, Dash, html, State
from dash.dcc import Dropdown
import dash_bootstrap_components as dbc
from numpy import std



GRAPH = {
    'a': ['b'],
    'b': [],
}

INDEX = {
    '0': 'a',
    '1': 'b',
}

class GraphBuilder:
    current_id = 'b'

    def __init__(self) -> None:
        global GRAPH, INDEX
        self.graph = GRAPH
        self.index = INDEX
        self.len = len(self.graph.keys())

    def add_edge(self, new_edge: Tuple[str, str]):
        cause, _ = new_edge
        can_add, new_graph = self.can_add_edge(new_edge)
        if can_add:
            self.graph = new_graph
            next_index = list(self.index.keys())[-1]
            next_index = int(next_index) + 1
            self.index[str(next_index)] = cause
            self.len += 1
        else:
            raise Exception("cannot add this edge -> no cycles allowed")

    def can_add_edge(self, new_edge: Tuple[str, str]):
        cause, effect = new_edge
        graph_copy = self.graph.copy()
        if (g:=graph_copy.get(cause, None)) is not None:
            g.append(effect)
        else:
            graph_copy.update({cause: [effect]})

        if (g:=graph_copy.get(effect, None)) is None:
            graph_copy.update({effect: []})

        return GraphBuilder.is_cyclic(graph_copy), graph_copy

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
        self.graph[GraphBuilder.current_id] = []
        self.index[index] = GraphBuilder.current_id
            

class NodeComponent(html.Div):
    def __init__(self, cause, effects):
        super().__init__(id="", children=None)
        self.id = {"type": "node", "index": cause} 
        self.style = {
            'border': '2px black solid',
            'margin': '2px'
        }
        self.label = cause
        self.children = [
            html.Div([
                html.P(f"variable: {cause}"),
                html.P(f"effects: {', '.join(effects) if effects else 'None'}"),
                html.P(id={"type": "textbox", "index": cause}),
                html.Button("-node", id={"type": "rem-node", "index": cause},
                            n_clicks=0),
                html.Button("+edge", id={"type": "add-edge", "index": cause},
                            n_clicks=0),
                html.Button("-node", id={"type": "rem-edge", "index": cause},
                            n_clicks=0),
            ], style={'margin': '4px'})
        ]




graph_builder = GraphBuilder()
class GraphBuilderComponent(html.Div):
    def __init__(self, id, style=None):
        global graph_builder
        super().__init__(id=id, style=style)
        self.graph_builder = graph_builder
        self.children = [dbc.Row()]
        self.children[0].children = []
        self.style = {
            'border': '2px black solid',
            'margin': '2px'
        }
        for cause, effects in self.graph_builder.graph.items():
            new_node = NodeComponent(cause, effects)
            self.children[0].children.append(dbc.Col(new_node))
        for _ in range(3 - self.graph_builder.len):
            self.children[0].children.append(dbc.Col(""))

    def add_node(self, index):
        self.graph_builder.new_node(index)
        var_name = list(self.graph_builder.graph.keys())[-1]
        new_node = NodeComponent(var_name, [])
        current_row = self.children[-1]
        assert current_row.children is not None, ""
        new_node_added = False
        for col in current_row.children:
            if col.children is not None and col.children == "":
                col.children = new_node
                new_node_added = True
                break
        if not new_node_added:
            new_row = dbc.Row()
            new_row.children = []
            new_row.children.append(dbc.Col(new_node))
            for _ in range(2):
                new_row.children.append(dbc.Col(""))
            self.children.append(new_row)

    def add_edge(self):
        pass

    def remove_node(self, node):
        print(f"removing: {node}")
        pass

    def remove_edge(self):
        pass


graph_builder_component = GraphBuilderComponent(id='graph-builder-component')

@callback(
    Output({"type": "textbox", "index": MATCH}, "children"),
    State({"type": "node", "index": MATCH}, "id"),
    Input({"type": "rem-node", "index": MATCH}, "n_clicks")
)
def abc(state, n_clicks):
    if n_clicks == 0:
        return
    global graph_builder_component
    node = state.get("index", "ERROR")
    graph_builder_component.remove_node(node)
    return f"{node}: {n_clicks}"

########################################
#                                      #
# HOW IT SHOULD BE USED IN A MAIN FILE #
#                                      #
########################################
app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.layout = html.Div([
    html.Div("graph builder"),
    html.Hr(),
    html.Div([
        dbc.Row([
            dbc.Col(
                dbc.Row([
                    graph_builder_component,
                    html.Label("Add Node"),
                    html.Button(id='add-node-button', children="Add Node",
                                n_clicks=1)
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
    if index == 1:
        # dont fire on start
        return current_state
    global graph_builder_component
    graph_builder_component.add_node(index)
    # graph_builder.new_node(str(index))
    # print(graph_builder.current_id)
    # print(graph_builder.index)
    return graph_builder_component.children

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