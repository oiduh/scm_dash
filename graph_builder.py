from typing import Tuple, Dict, Set
from dash import ALL, callback, Input, Output, Dash, html, State, ctx
from dash.dcc import Dropdown
import dash_bootstrap_components as dbc
from copy import deepcopy
from dash_cytoscape import Cytoscape


GRAPH: Dict[str, Set[str]] = {
    'a': set('b'),
    'b': set(),
}


class GraphTracker:
    out_edges: Dict[str, Set[str]] = dict()
    in_edges: Dict[str, Set[str]] = dict()
    aliases: Dict[str, str] = dict()

graph_tracker = GraphTracker()
graph_tracker.out_edges.update({"a": set("b"), "b": set()})
graph_tracker.in_edges.update({"a": set(), "b": set("a")})


class GraphBuilder:
    current_id = "b"

    def __init__(self) -> None:
        global graph_tracker
        self.graph_tracker = graph_tracker
        self.len = len(self.graph_tracker.out_edges.keys())

    def add_edge(self, new_edge: Tuple[str, str]) -> bool:
        can_add, out_graph, in_graph = self.can_add_edge(new_edge)
        if can_add:
            self.graph_tracker.out_edges = out_graph
            self.graph_tracker.in_edges = in_graph
            self.len += 1
        return can_add

    def can_add_edge(self, new_edge: Tuple[str, str]):
        cause, effect = new_edge
        assert cause in self.graph_tracker.out_edges
        assert cause in self.graph_tracker.in_edges
        assert effect in self.graph_tracker.out_edges
        assert effect in self.graph_tracker.in_edges

        out_copy = deepcopy(self.graph_tracker.out_edges)
        in_copy = deepcopy(self.graph_tracker.in_edges)
        if (g:=out_copy.get(cause)) is not None and effect in g:
            return False, out_copy, in_copy

        # at this point add edges to the graph copies and check for cycles
        # before returning values

        effects = out_copy.get(cause)
        causes = in_copy.get(effect)
        assert effects and causes

        effects.add(effect)
        out_copy.update({cause: effects})
        causes.add(cause)
        in_copy.update({effect: causes})

        return GraphBuilder.is_cyclic(out_copy), out_copy, in_copy


assert False, "TODO: continue refactoring here"

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

    def new_node(self):
        if GraphBuilder.current_id[-1] == 'z':
            GraphBuilder.current_id += 'a'
        else:
            cpy = GraphBuilder.current_id
            last = cpy[-1]
            new = cpy[:-1] + chr(ord(last) + 1)
            GraphBuilder.current_id = new
        self.graph[GraphBuilder.current_id] = set()

    def remove_node(self, node_to_remove):
        assert node_to_remove in self.graph, "error"
        print(f"before: {self.graph}")
        self.graph.pop(node_to_remove, None)
        for _, effects in self.graph.items():
            if node_to_remove in effects:
                effects.discard(node_to_remove)
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
        self.children = [
            html.Div([], id="node-container"),
            html.Button(id='add-node-button', children="Add Node",
                        n_clicks=1),
            html.Button(id='reset-graph-builder', children="Reset Graph Builder",
                        n_clicks=1),
        ]
        self.style = {
            'border': '2px black solid',
            'margin': '2px'
        }
        for cause, effects in self.graph_builder.graph.items():
            new_node = NodeComponent(cause, effects)
            self.children[0].children.append(new_node)

    def add_node(self):
        self.graph_builder.new_node()
        var_name = list(self.graph_builder.graph.keys())[-1]
        new_node = NodeComponent(var_name, set())
        self.children[0].children.append(new_node)

    def add_edge(self, source_node, target_node):
        edge = source_node, target_node
        assert self.graph_builder.add_edge(edge), "fatal error"
        new_effects = self.graph_builder.graph.get(source_node)
        assert new_effects is not None, "fatal error"
        for idx, node_component in enumerate(self.children[0].children):
            if node_component.label == source_node:
                self.children[0].children[idx] = NodeComponent(source_node, new_effects)

    def remove_node(self, node_to_remove):
        print(self.children[0].children)
        for idx, node in enumerate(self.children[0].children):
            assert isinstance(node, NodeComponent), "error"
            if node.label == node_to_remove:
                self.graph_builder.remove_node(node_to_remove)
                self.children[0].children[idx:] = self.children[0].children[(idx+1):]
                break
        for idx, node in enumerate(self.children[0].children):
            assert isinstance(node, NodeComponent), "error"
            updated_effects = self.graph_builder.graph.get(node.label)
            assert updated_effects is not None, "error"
            self.children[0].children[idx] = NodeComponent(node.label, updated_effects)

    def remove_edge(self, source_node, target_node):
        self.graph_builder.remove_edge(source_node, target_node)
        for idx, node in enumerate(self.children[0].children):
            assert isinstance(node, NodeComponent), "error"
            updated_effects = self.graph_builder.graph.get(node.label)
            assert updated_effects is not None, "error"
            self.children[0].children[idx] = NodeComponent(node.label, updated_effects)


graph_builder_component = GraphBuilderComponent(id='graph-builder-component')

class GraphBuilderView(html.Div):
    def __init__(self, id):
        super().__init__(id)
        self.style = {
            'border': '2px black solid',
            'margin': '2px'
        }
        self.children = [
            Cytoscape(
                id="network-graph", layout={"name": "circle"},
                userPanningEnabled=False,
                zoomingEnabled=False,
                # TODO: use stylesheets for arrows and style
                # give attributes to nodes (cause/effect)
                # assign actual mechanism to edges
                # different colors for special nodes/edges
                style={"width": "100%", "height": "700px"},
                elements=[],
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
                ]
            ),
            html.Button("Reset View", id="graph-view-reset", n_clicks=0)
        ]
graph_builder_view = GraphBuilderView(id="graph-builder-view")

