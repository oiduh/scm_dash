from copy import deepcopy
import string


class CONSTANTS:
    IDS = {letter for letter in string.ascii_lowercase}
    MAX_NODES = len(IDS)


class GraphTracker:
    out_edges: dict[str, set[str]] = dict()
    in_edges: dict[str, set[str]] = dict()
    aliases: dict[str, str] = dict()


# initial minimal graph settings -> 2 nodes, where 'a' affects 'b'
graph_tracker = GraphTracker()
graph_tracker.out_edges.update({"a": set("b"), "b": set()})
graph_tracker.in_edges.update({"a": set(), "b": set("a")})


class GraphBuilder:
    def __init__(self) -> None:
        global graph_tracker
        self.graph_tracker = graph_tracker
        self.len = len(self.graph_tracker.out_edges.keys())

    def add_edge(self, source_node: str, target_node: str):
        can_add, out_, in_ = self.can_add_edge(source_node, target_node)
        if can_add:
            self.graph_tracker.out_edges = out_
            self.graph_tracker.in_edges = in_
            self.len += 1
        return can_add

    def can_add_edge(self, source_node: str, target_node: str):
        assert source_node in self.graph_tracker.out_edges
        assert source_node in self.graph_tracker.in_edges
        assert target_node in self.graph_tracker.out_edges
        assert target_node in self.graph_tracker.in_edges

        out_copy = deepcopy(self.graph_tracker.out_edges)
        in_copy = deepcopy(self.graph_tracker.in_edges)
        if (g:=out_copy.get(source_node)) is not None and target_node in g:
            return False, out_copy, in_copy

        effects = out_copy.get(source_node)
        causes = in_copy.get(target_node)
        assert effects is not None and causes is not None

        effects.add(target_node)
        out_copy.update({source_node: effects})
        causes.add(source_node)
        in_copy.update({target_node: causes})

        return not self.is_cyclic(out_copy), out_copy, in_copy

    def is_cyclic_util(
        self, node: str, visited: dict[str, bool], rec_stack: dict[str, bool],
        graph: dict[str, set[str]]
    ):
        visited[node] = True
        rec_stack[node] = True
        for neighbor in graph[node]:
            if not visited[neighbor]:
                if self.is_cyclic_util(neighbor, visited, rec_stack, graph):
                    return True
            elif rec_stack[neighbor]:
                return True
        rec_stack[node] = False
        return False

    def is_cyclic(self, out_nodes: dict[str, set[str]]):
        visited = {k: False for k in out_nodes.keys()}
        rec_stack = {k: False for k in out_nodes.keys()}

        for node in out_nodes.keys():
            if not visited[node]:
                if self.is_cyclic_util(node, visited, rec_stack, out_nodes):
                    return True
        return False

    def new_node(self):
        current_nodes = set(self.graph_tracker.out_edges.keys())

        free_nodes = CONSTANTS.IDS.difference(current_nodes)
        if not free_nodes:
            return

        next_node = list(sorted(free_nodes))[0]
        self.graph_tracker.out_edges.update({next_node: set()})
        self.graph_tracker.in_edges.update({next_node: set()})

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
        s_out = source_node in self.graph_tracker.out_edges.keys()
        t_out = target_node in self.graph_tracker.out_edges.keys()
        s_in = source_node in self.graph_tracker.in_edges.keys()
        t_in = target_node in self.graph_tracker.in_edges.keys()
        assert all([s_out, t_out, s_in, t_in]), "error"

        tmp_out = self.graph_tracker.out_edges.get(source_node)
        assert tmp_out is not None and target_node in tmp_out, "error"
        tmp_out.discard(target_node)
        self.graph_tracker.out_edges.update({source_node: tmp_out})

        tmp_in  = self.graph_tracker.in_edges.get(target_node)
        assert tmp_in is not None and source_node in tmp_in, "error"
        tmp_in.discard(source_node)
        self.graph_tracker.in_edges.update({target_node: tmp_in})

