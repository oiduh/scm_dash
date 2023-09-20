from typing import Tuple, List, Dict, Set
from dash import ALL, MATCH, callback, Input, Output, Dash, html, State, ctx
from dash.dcc import Dropdown
import dash_bootstrap_components as dbc
from copy import deepcopy
from dash_cytoscape import Cytoscape



GRAPH: Dict[str, Set[str]] = {
    'a': set('b'),
    'b': set(),
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

    def add_edge(self, new_edge: Tuple[str, str]) -> bool:
        cause, _ = new_edge
        can_add, new_graph = self.can_add_edge(new_edge)
        if can_add:
            self.graph = new_graph
            next_index = list(self.index.keys())[-1]
            next_index = int(next_index) + 1
            self.index[str(next_index)] = cause
            self.len += 1
        return can_add

    def can_add_edge(self, new_edge: Tuple[str, str]):
        cause, effect = new_edge
        graph_copy = deepcopy(self.graph)

        if cause in self.graph and effect in self.graph[cause]:
            return False, graph_copy

        if (g:=graph_copy.get(cause, None)) is not None:
            assert isinstance(g, set), "error"
            g.add(effect)
        else:
            graph_copy.update({cause: set(effect)})

        # if adding node alwasy succeeds, this might be redundant
        if (g:=graph_copy.get(effect, None)) is None:
            graph_copy.update({effect: set()})

        return not GraphBuilder.is_cyclic(graph_copy), graph_copy

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
        self.graph[GraphBuilder.current_id] = set()
        self.index[index] = GraphBuilder.current_id

    def remove_node(self, node_to_remove):
        assert node_to_remove in self.graph, "error"
        assert node_to_remove in self.index.values(), "error"
        print(f"before: {self.graph}")
        self.graph.pop(node_to_remove, None)
        for _, effects in self.graph.items():
            if node_to_remove in effects:
                effects.discard(node_to_remove)
        for index, node in self.index.items():
            if node_to_remove == node:
                self.index.pop(index, None)
                break
        print(f"after: {self.graph}")

    def remove_edge(self, source_node, target_node):
        x = self.graph.get(source_node)
        assert x is not None, "error"
        x.discard(target_node)


class NodeComponent(html.Div):
    def __init__(self, cause: str, effects: Set[str]):
        global graph_builder
        super().__init__(id="", children=None)
        self.graph_builder = graph_builder
        self.id = {"type": "node", "index": cause} 
        self.style = {
            'border': '2px black solid',
            'margin': '2px'
        }
        self.label = cause
        self.effects = html.P(f"effects: {', '.join(effects) if effects else 'None'}")

        self.children = [
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.P(f"variable: {cause}"),
                        self.effects,
                        html.Button("-node", id={"type": "rem-node", "index": cause},
                                    n_clicks=0),
                    ]),
                    dbc.Col([
                        Dropdown(options=[], placeholder='select node',
                                 id={"type": "valid-edges-add", "index": cause}),
                        html.Button("+edge", id={"type": "add-edge", "index": cause},
                                    n_clicks=0),
                    ]),
                    dbc.Col([
                        Dropdown(options=[], placeholder='select node',
                                 id={"type": "valid-edges-rem", "index": cause}),
                        html.Button("-edge", id={"type": "rem-edge", "index": cause},
                                    n_clicks=0),
                    ])
                ]),
            ], style={'margin': '4px'})
        ]


graph_builder = GraphBuilder()
class GraphBuilderComponent(html.Div):
    def __init__(self, id, style=None):
        global graph_builder
        super().__init__(id=id, style=style)
        self.graph_builder = graph_builder
        self.children: List[NodeComponent] = []
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
        new_node = NodeComponent(var_name, set())
        self.children.append(new_node)

    def add_edge(self, source_node, target_node):
        edge = source_node, target_node
        assert self.graph_builder.add_edge(edge), "fatal error"
        new_effects = self.graph_builder.graph.get(source_node)
        assert new_effects is not None, "fatal error"
        for idx, node_component in enumerate(self.children):
            if node_component.label == source_node:
                self.children[idx] = NodeComponent(source_node, new_effects)

    def remove_node(self, node_to_remove):
        for idx, node in enumerate(self.children):
            assert isinstance(node, NodeComponent), "error"
            if node.label == node_to_remove:
                self.graph_builder.remove_node(node_to_remove)
                self.children[idx:] = self.children[(idx+1):]
                break
        for idx, node in enumerate(self.children):
            assert isinstance(node, NodeComponent), "error"
            updated_effects = self.graph_builder.graph.get(node.label)
            assert updated_effects is not None, "error"
            self.children[idx] = NodeComponent(node.label, updated_effects)

    def remove_edge(self, source_node, target_node):
        self.graph_builder.remove_edge(source_node, target_node)
        for idx, node in enumerate(self.children):
            assert isinstance(node, NodeComponent), "error"
            updated_effects = self.graph_builder.graph.get(node.label)
            assert updated_effects is not None, "error"
            self.children[idx] = NodeComponent(node.label, updated_effects)


graph_builder_component = GraphBuilderComponent(id='graph-builder-component')


########################################
#                                      #
# HOW IT SHOULD BE USED IN A MAIN FILE #
#                                      #
########################################
app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
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
            dbc.Col(
                html.Div(
                    Cytoscape(id="network-graph", layout={"name": "grid"},
                              # TODO: use stylesheets for arrows and style
                              # give attributes to nodes (cause/effect)
                              # assign actual mechanism to edges
                              # different colors for special nodes/edges
                              style={"width": "100%", "height": "400px"},
                              elements=[
                              # nodes
                              {"data": {"id": "one", "label": "node1"}},
                              {"data": {"id": "two", "label": "node2"}},
                              {"data": {"id": "three", "label": "node3"}},
                              {"data": {"id": "four", "label": "node4"}},
                              # edges
                              {"data": {"source": "one", "target": "two"}},
                              {"data": {"source": "two", "target": "three"}},
                              {"data": {"source": "three", "target": "four"}},
                              {"data": {"source": "one", "target": "three"}},
                              ],
                              stylesheet=[
                              {
                              "selector": "node",
                              "style": {
                              "label": "data(label)"
                              }
                              },
                              {
                              "selector": "edge",
                              "style": {
                              "curve-style": "bezier",
                              "target-arrow-shape": "triangle",
                              "arrow-scale": 2
                              }
                              }
                              ])
                )
            )
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
    prevent_initial_call=True
)
def add_new_node(index):
    global graph_builder_component
    if ctx.triggered_id == "add-node-button":
        graph_builder_component.add_node(index)
    return graph_builder_component.children

@callback(
    Output("graph-builder-component", "children", allow_duplicate=True),
    Input({"type": "rem-node", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def remove_node(x):
    global graph_builder_component
    triggered_node = ctx.triggered_id
    triggered_node = triggered_node and triggered_node.get("index", None)
    if sum(x) > 0 and triggered_node is not None:
        graph_builder_component.remove_node(triggered_node)
    return graph_builder_component.children

@callback(
    Output("graph-builder-component", "children", allow_duplicate=True),
    State({"type": "valid-edges-add", "index": ALL}, "value"),
    Input({"type": "add-edge", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def add_new_edge(state, input):
    if sum(input) == 0:
        raise Exception("not clicked add edge")

    global graph_builder_component
    triggered_node = ctx.triggered_id
    if triggered_node and triggered_node["type"] == "add-edge":
        source_node = triggered_node["index"]
        target_node = list(filter(lambda x: x is not None, state))
        target_node = target_node[0]
        print(f"registering add: source={source_node}, target={target_node}")
        graph_builder_component.add_edge(source_node, target_node)

    return graph_builder_component.children

@callback(
    Output("graph-builder-component", "children", allow_duplicate=True),
    State({"type": "valid-edges-rem", "index": ALL}, "value"),
    Input({"type": "rem-edge", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def remove_edge(state, input):
    if sum(input) == 0:
        raise Exception("not clicked remove edge")

    global graph_builder_component
    triggered_node = ctx.triggered_id
    if triggered_node and triggered_node["type"] == "rem-edge":
        source_node = triggered_node["index"]
        target_node = list(filter(lambda x: x is not None, state))
        target_node = target_node[0] if target_node else None
        if target_node is not None:
            print(f"registering remove: source={source_node}, target={target_node}")
            graph_builder_component.remove_edge(source_node, target_node)

    return graph_builder_component.children

@callback(
    Output({"type": "valid-edges-add", "index": ALL}, "options"),
    Output({"type": "valid-edges-rem", "index": ALL}, "options"),
    Input('graph-builder-component', 'children'),
    prevent_initial_call=True
)
def update_edge_dropdowns(_):
    global graph_builder_component
    can_be_added = []
    can_be_removed = []
    all_nodes = graph_builder_component.graph_builder.graph.keys()
    for node_i in all_nodes:
        can_be_added.append([])
        for node_j in all_nodes:
            edge = node_i, node_j
            can_add, _ = graph_builder_component.graph_builder.can_add_edge(edge)
            potential_effect = {"label": node_j, "value": node_j, "disabled": not can_add}
            can_be_added[-1].append(potential_effect)
        can_be_removed.append([])
        effects = graph_builder_component.graph_builder.graph.get(node_i)
        assert effects is not None, "error"
        for effect in effects:
            removable = {"label": effect, "value": effect}
            can_be_removed[-1].append(removable)

    return can_be_added, can_be_removed

if __name__ == '__main__':
    app.run(debug=True,)
