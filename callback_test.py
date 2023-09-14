from typing import Tuple, List
from dash import ALL, MATCH, callback, Input, Output, Dash, html, State, ctx
from dash.dcc import Dropdown
import dash_bootstrap_components as dbc



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
                html.Button("-edge", id={"type": "rem-edge", "index": cause},
                            n_clicks=0),
            ], style={'margin': '4px'})
        ]




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
            new_node = NodeComponent(cause, effects)
            self.children.append(new_node)

    def add_node(self, index):
        self.graph_builder.new_node(index)
        var_name = list(self.graph_builder.graph.keys())[-1]
        new_node = NodeComponent(var_name, [])
        self.children.append(new_node)

    def add_edge(self):
        pass

    def remove_node(self, node_to_remove):
        for idx, node in enumerate(self.children):
            assert isinstance(node, NodeComponent), "error"
            print(f"{node.label} - {node_to_remove}")
            if node.label == node_to_remove:
                print(f"removing: {node.label}")
                self.children[idx:] = self.children[(idx+1):]
                break



    def remove_edge(self):
        pass


graph_builder_component = GraphBuilderComponent(id='graph-builder-component')


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
    Output('graph-builder-component', 'children', allow_duplicate=True),
    Input('add-node-button', 'n_clicks'),
    State('graph-builder-component', 'children'),
    prevent_initial_call=True
)
def add_new_node(index, current_state):
    global graph_builder_component
    graph_builder_component.add_node(index)
    return graph_builder_component.children

@callback(
    # Output({"type": "textbox", "index": MATCH}, "children"),
    Output("graph-builder-component", "children", allow_duplicate=True),
    Input({"type": "rem-node", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def remove_node(x):
    global graph_builder_component

    if sum(x) == 0:
        return graph_builder_component.children

    triggered_node = ctx.triggered_id
    if triggered_node and (node:=triggered_node.get("index", None)):
        print(f"remove: {node}")
        graph_builder_component.remove_node(node)


    # node = state.get("index", "ERROR")
    # graph_builder_component.remove_node(node_to_remove)
    return graph_builder_component.children


if __name__ == '__main__':
    app.run(debug=True,)
