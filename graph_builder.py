from typing import Tuple, Dict, Set
from dash import ALL, callback, Input, Output, Dash, html, State, ctx
from dash.dcc import Dropdown
import dash_bootstrap_components as dbc
from copy import deepcopy
from dash_cytoscape import Cytoscape


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
        assert effects is not None and causes is not None

        effects.add(effect)
        out_copy.update({cause: effects})
        causes.add(cause)
        in_copy.update({effect: causes})

        return not GraphBuilder.is_cyclic(out_copy), out_copy, in_copy

    @staticmethod
    def is_cyclic_util(node: str, visited: Dict[str, bool],
                       rec_stack: Dict[str, bool], graph: Dict[str, Set[str]]):
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
    def is_cyclic(out_nodes: Dict[str, Set[str]]):
        visited = {k: False for k in out_nodes.keys()}
        rec_stack = {k: False for k in out_nodes.keys()}

        for node in out_nodes.keys():
            if not visited[node]:
                if GraphBuilder.is_cyclic_util(node, visited, rec_stack, out_nodes):
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
        
        self.graph_tracker.out_edges.update({GraphBuilder.current_id: set()})
        self.graph_tracker.in_edges.update({GraphBuilder.current_id: set()})

    def remove_node(self, node_to_remove: str):
        out_edges_check = node_to_remove in self.graph_tracker.out_edges
        in_edges_check = node_to_remove in self.graph_tracker.in_edges
        assert out_edges_check and in_edges_check, "node does not exist"
        self.graph_tracker.out_edges.pop(node_to_remove)
        self.graph_tracker.in_edges.pop(node_to_remove)
        for node in self.graph_tracker.out_edges.keys():
            tmp_out = self.graph_tracker.out_edges.get(node)
            tmp_in = self.graph_tracker.in_edges.get(node)
            assert tmp_out is not None and tmp_in is not None, "error"
            tmp_out.discard(node_to_remove)
            tmp_in.discard(node_to_remove)
            self.graph_tracker.out_edges.update({node: tmp_out})
            self.graph_tracker.in_edges.update({node: tmp_in})

    def remove_edge(self, source_node: str, target_node: str):
        a = source_node in self.graph_tracker.out_edges.keys()
        b = target_node in self.graph_tracker.out_edges.keys()
        c = source_node in self.graph_tracker.in_edges.keys()
        d = target_node in self.graph_tracker.in_edges.keys()
        assert all([a, b, c, d]), "error"
        tmp_out = self.graph_tracker.out_edges.get(source_node)
        assert tmp_out is not None and target_node in tmp_out, "error"
        tmp_out.discard(target_node)
        self.graph_tracker.out_edges.update({source_node: tmp_out})

        tmp_in  = self.graph_tracker.in_edges.get(target_node)
        assert tmp_in is not None and source_node in tmp_in, "error"
        tmp_in.discard(source_node)
        self.graph_tracker.in_edges.update({target_node: tmp_in})


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
        # for cause, effects in self.graph_builder.graph.items():
        for cause, effects in self.graph_builder.graph_tracker.out_edges.items():
            new_node = NodeComponent(cause, effects)
            self.children[0].children.append(new_node)

    def add_node(self):
        self.graph_builder.new_node()
        var_name = list(self.graph_builder.graph_tracker.out_edges.keys())[-1]
        new_node = NodeComponent(var_name, set())
        self.children[0].children.append(new_node)

    def add_edge(self, source_node, target_node):
        edge = source_node, target_node
        assert self.graph_builder.add_edge(edge), "fatal error"
        new_effects = self.graph_builder.graph_tracker.out_edges.get(source_node)
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
            updated_effects = self.graph_builder.graph_tracker.out_edges.get(node.label)
            assert updated_effects is not None, "error"
            self.children[0].children[idx] = NodeComponent(node.label, updated_effects)

    def remove_edge(self, source_node, target_node):
        self.graph_builder.remove_edge(source_node, target_node)
        for idx, node in enumerate(self.children[0].children):
            assert isinstance(node, NodeComponent), "error"
            updated_effects = self.graph_builder.graph_tracker.out_edges.get(node.label)
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


if __name__ == "__main__":
    x = graph_builder

    print(x.graph_tracker.out_edges)
    print(x.graph_tracker.in_edges)
    print()

    x.new_node()
    print(x.graph_tracker.out_edges)
    print(x.graph_tracker.in_edges)
    print()

    x.new_node()
    print(x.graph_tracker.out_edges)
    print(x.graph_tracker.in_edges)
    print()

    x.add_edge(("a", "c"))
    x.add_edge(("a", "d"))
    print(x.graph_tracker.out_edges)
    print(x.graph_tracker.in_edges)
    print()

    x.remove_edge("a", "b")
    print(x.graph_tracker.out_edges)
    print(x.graph_tracker.in_edges)
