import string
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Literal

from models.mechanism import MechanismMetadata
from models.noise import Noise


@dataclass
class Node:
    id_: str
    name: str  # TODO: custom node name
    graph: "Graph"
    in_nodes: list["Node"] = field(default_factory=list)
    out_nodes: list["Node"] = field(default_factory=list)
    noise: Noise = field(init=False)
    mechanism_metadata: MechanismMetadata = field(
        default_factory=MechanismMetadata,
    )

    def __post_init__(self) -> None:
        self.noise = Noise.default_noise(self.id_)

    def get_in_node_ids(self) -> list[str]:
        return [n.id_ for n in self.in_nodes]

    def get_out_node_ids(self) -> list[str]:
        return [n.id_ for n in self.out_nodes]

    def add_in_node(self, to_add: "Node") -> None:
        """
        Exception:
            target node already an in node
        """
        if to_add in self.in_nodes:
            raise Exception("Node already an in_node")
        self.in_nodes.append(to_add)

    def add_out_node(self, to_add: "Node") -> None:
        """
        Exception:
            target node already an out node
        """
        if to_add in self.out_nodes:
            raise Exception("Node already an out_node")
        self.out_nodes.append(to_add)

    def remove_in_node(self, to_remove: "Node") -> None:
        """
        Exception:
            target node not an in node
        """
        if to_remove.id_ not in self.get_in_node_ids():
            raise Exception("Target node is not an in node")
        self.in_nodes.remove(to_remove)

    def remove_out_node(self, to_remove: "Node") -> None:
        """
        Exception:
            target node not an out node
        """
        if to_remove.id_ not in self.get_out_node_ids():
            raise Exception("Target node is not an out node")
        self.out_nodes.remove(to_remove)

    def change_mechanism_type(
        self, new_mechanism: Literal["regression", "classification"]
    ) -> None:
        self.mechanism_metadata.change_type(new_mechanism)


@dataclass
class Graph:
    nodes: dict[str, Node | None] = field(
        default_factory=lambda: {str(id): None for id in string.ascii_lowercase}
    )

    def get_nodes(self) -> list[Node]:
        return [node for node in self.nodes.values() if node]

    def get_node_ids(self) -> list[str]:
        return [node.id_ for node in self.get_nodes()]

    def get_node_names(self) -> list[str]:
        return [node.name for node in self.get_nodes()]

    def get_node_by_id(self, id_: str) -> Node | None:
        return self.nodes.get(id_)

    def get_node_by_name(self, name: str) -> Node | None:
        nodes = (node for node in self.get_nodes() if node.name == name)
        return next(nodes, None)

    def get_free_node_id(self) -> str | None:
        free_node_ids = (id for id, node in self.nodes.items() if node is None)
        return next(free_node_ids, None)

    def add_node(self) -> None:
        free_node_id = self.get_free_node_id()
        if free_node_id is None:
            raise Exception("Cannot add another node")

        new_node = Node(free_node_id, free_node_id, self)
        self.nodes[free_node_id] = new_node
        new_node.mechanism_metadata.change_type("regression")

    def remove_node(self, to_remove: Node) -> None:
        """
        Exception:
            node does not exist
        """
        if self.nodes.get(to_remove.id_) is None:
            raise Exception("Node does not exist")

        for node in self.get_nodes():
            if to_remove.id_ in [n.id_ for n in node.in_nodes]:
                node.remove_in_node(to_remove)
            if to_remove.id_ in [n.id_ for n in node.out_nodes]:
                node.remove_out_node(to_remove)

        self.nodes[to_remove.id_] = None

    def add_edge(self, source: Node, target: Node) -> None:
        if self.can_add_edge(source, target) is False:
            raise Exception("Cannot add edge")

        source.add_out_node(target)
        target.add_in_node(source)

    def can_add_edge(self, source: Node, target: Node) -> bool:
        target_in_nodes = target.get_in_node_ids()
        source_out_nodes = source.get_out_node_ids()
        if source.id_ in target_in_nodes and target.id_ in source_out_nodes:
            return False

        new_graph = deepcopy(self)
        new_source = new_graph.get_node_by_id(source.id_)
        new_target = new_graph.get_node_by_id(target.id_)
        assert new_source is not None and new_target is not None
        new_source.add_out_node(new_target)
        new_target.add_in_node(new_source)

        return not Graph.is_cyclic(new_graph)

    @staticmethod
    def is_cyclic(new_graph: "Graph") -> bool:
        nodes = new_graph.get_nodes()
        visited = {k.id_: False for k in nodes}
        recursive_stack = {k.id_: False for k in nodes}

        for node in nodes:
            if visited[node.id_] is False:
                if Graph.is_cyclic_util(node, visited, recursive_stack, new_graph):
                    return True
        return False

    @staticmethod
    def is_cyclic_util(
        node: Node,
        visited: dict[str, bool],
        recursive_stack: dict[str, bool],
        new_graph: "Graph",
    ) -> bool:
        visited[node.id_] = True
        recursive_stack[node.id_] = True
        for neighbor in node.out_nodes:
            if not visited[neighbor.id_]:
                if Graph.is_cyclic_util(neighbor, visited, recursive_stack, new_graph):
                    return True
            elif recursive_stack[neighbor.id_]:
                return True
        recursive_stack[node.id_] = False
        return False

    def remove_edge(self, source: Node, target: Node) -> None:
        """
        Exception:
            edge cannot be removed
        """
        if self.can_remove_edge(source, target) is False:
            raise Exception("Cannot remove edge")

        source.out_nodes.remove(target)
        target.in_nodes.remove(source)

    def can_remove_edge(self, source: Node, target: Node) -> bool:
        source_removable = source.id_ in [n.id_ for n in target.in_nodes]
        target_removable = target.id_ in [n.id_ for n in source.out_nodes]
        return source_removable and target_removable


# TODO: initial graph setup -> replace with imported settings if available
graph = Graph()
graph.add_node()
graph.add_node()
a = graph.get_node_by_id("a")
b = graph.get_node_by_id("b")
assert a is not None and b is not None, "Failed at init"
graph.add_edge(a, b)
