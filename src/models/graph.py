from dataclasses import dataclass, field
from plotly.basedatatypes import deepcopy
import string
from models.noise import Data


@dataclass
class Node:
    id: str
    name: str
    in_nodes: list['Node']
    out_nodes: list['Node']
    data: Data = field(init=False)

    def __post_init__(self):
        self.data = Data.default_data(self.id)

    def get_in_node_ids(self):
        return [n.id for n in self.in_nodes]

    def get_out_node_ids(self):
        return [n.id for n in self.out_nodes]

    def add_in_node(self, to_add: 'Node'):
        assert to_add not in self.in_nodes, "Node already an in_node"
        self.in_nodes.append(to_add)

    def add_out_node(self, to_add: 'Node'):
        assert to_add not in self.out_nodes, "Node already an out_node"
        self.out_nodes.append(to_add)

    def remove_in_node(self, to_remove: 'Node'):
        assert to_remove.id in [n.id for n in self.in_nodes], "target node is not an in node"
        self.in_nodes.remove(to_remove)

    def remove_out_node(self, to_remove: 'Node'):
        assert to_remove.id in [n.id for n in self.out_nodes], "target node is not an out node"
        self.out_nodes.remove(to_remove)


@dataclass
class Graph:
    nodes: dict[str, Node | None] = field(
        default_factory=lambda: {str(id): None for id in string.ascii_lowercase}
    )

    def get_nodes(self):
        return [node for node in self.nodes.values() if node]

    def get_node_ids(self):
        return [node.id for node in self.get_nodes()]

    def get_node_names(self):
        return [node.name for node in self.get_nodes()]

    def get_node_by_id(self, id: str):
        assert self.nodes.get(id), "Node does not exist"
        return [node for node in self.get_nodes() if node.id == id][0]

    def get_node_by_name(self, name: str):
        assert name in self.get_node_names(), "Node does not exist"
        return [node for node in self.get_nodes() if node.name == name][0]

    def get_free_node_id(self):
        free_node_ids = [id for id in self.nodes.keys() if not self.nodes.get(id)]
        return free_node_ids[0] if free_node_ids else None

    def add_node(self):
        free_node_id = self.get_free_node_id()
        assert free_node_id, "No more space for new nodes"
        new_node = Node(free_node_id, free_node_id, list(), list())
        self.nodes[free_node_id] = new_node

    def remove_node(self, to_remove: Node):
        assert self.nodes.get(to_remove.id), "Node does not exist"
        for node in self.get_nodes():
            if to_remove.id in [n.id for n in node.in_nodes]:
                node.remove_in_node(to_remove)
            if to_remove.id in [n.id for n in node.out_nodes]:
                node.remove_out_node(to_remove)
        self.nodes[to_remove.id] = None

    def add_edge(self, source: Node, target: Node):
        if self.can_add_edge(source, target):
            self.get_node_by_id(source.id).add_out_node(target)
            self.get_node_by_id(target.id).add_in_node(source)

    def can_add_edge(self, source: Node, target: Node):
        # assert self.nodes.get(source.id), "Node must exist in graph"
        # assert self.nodes.get(target.id), "Node must exist in graph"

        target_in_nodes = [n.id for n in target.in_nodes]
        source_out_nodes = [n.id for n in source.out_nodes]
        if source.id in target_in_nodes or target.id in source_out_nodes:
            return False
        # assert source.id not in target_in_nodes, "source is already an in node"
        # assert target.id not in source_out_nodes, "target is already an out node"

        new_graph = deepcopy(self)
        new_graph.get_node_by_id(source.id).add_out_node(target)
        new_graph.get_node_by_id(target.id).add_in_node(source)

        return not Graph.is_cyclic(new_graph)

    @staticmethod
    def is_cyclic(new_graph: 'Graph'):
        nodes = new_graph.get_nodes()
        visited = {k.id: False for k in nodes}
        recursive_stack = {k.id: False for k in nodes}

        for node in nodes:
            if not visited[node.id]:
                if Graph.is_cyclic_util(node, visited, recursive_stack, new_graph):
                    return True
        return False

    @staticmethod
    def is_cyclic_util(node: Node, visited: dict[str, bool],
                       recursive_stack: dict[str, bool], new_graph: 'Graph'):
        visited[node.id] = True
        recursive_stack[node.id] = True
        for neighbor in new_graph.get_node_by_id(node.id).out_nodes:
            if not visited[neighbor.id]:
                if Graph.is_cyclic_util(neighbor, visited, recursive_stack, new_graph):
                    return True
            elif recursive_stack[neighbor.id]:
                return True
        recursive_stack[node.id] = False
        return False

    def remove_edge(self, source: Node, target: Node):
        if not self.can_remove_edge(source, target):
            return
        out_node = self.get_node_by_id(target.id)
        self.get_node_by_id(source.id).out_nodes.remove(out_node)
        in_node = self.get_node_by_id(source.id)
        self.get_node_by_id(target.id).in_nodes.remove(in_node)

    def can_remove_edge(self, source: Node, target: Node):
        target_in_nodes = [n.id for n in target.in_nodes]
        source_out_nodes = [n.id for n in source.out_nodes]
        return source.id in target_in_nodes and target.id in source_out_nodes


# TODO: initial graph setup -> replace with imported settings if available
graph = Graph()
graph.add_node()  # a
graph.add_node()  # b
graph.add_node()  # c
graph.add_node()  # d
graph.add_edge(graph.get_node_by_id('a'), graph.get_node_by_id('b'))
graph.add_edge(graph.get_node_by_id('c'), graph.get_node_by_id('d'))

