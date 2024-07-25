import string
from copy import deepcopy
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from models.mechanism import (
    ClassificationMechanism,
    MechanismMetadata,
    MechanismState,
    MechanismType,
    RegressionMechanism,
)
from models.noise import Noise


@dataclass
class Node:
    id_: str
    name: str  # TODO: custom node name
    graph: "Graph"

    in_nodes: list["Node"] = field(default_factory=list)
    out_nodes: list["Node"] = field(default_factory=list)
    noise: Noise = field(init=False)
    data: np.ndarray | None = None
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

    def change_type(self, new_type: MechanismType) -> None:
        assert self.mechanism_metadata.state == "editable"
        self.mechanism_metadata.mechanism_type = new_type
        self.mechanism_metadata.formulas = MechanismMetadata.reset_formulas()

    def formulas_are_valid(self) -> bool:
        # data in range (-5.0, 5.0)
        # just a sanity check, values might not be correct for actual outcome
        input_ids = []
        input_ids.append(f"n_{self.id_}")  # add noise to inputs as well
        input_ids.extend(self.get_in_node_ids())
        data = {node_id: (np.random.rand(1000) - 0.5) * 10 for node_id in input_ids}
        formulas = self.mechanism_metadata.get_formulas()
        match self.mechanism_metadata.mechanism_type:
            case "regression":
                mechanism = RegressionMechanism(list(formulas.values()), data)
            case "classification":
                mechanism = ClassificationMechanism(list(formulas.values()), data)
        # we do not care about the data, only if the data generation failed
        return mechanism.transform().error is None

    def change_state(self, new_state: MechanismState) -> None:
        """
        change state -> formulas editable or locked
        changing to the locked state requires a validation of the formulas
        Exception:
            failed to evaluate formula with dummy data
        """
        if new_state == "locked":
            if self.formulas_are_valid() is False:
                raise Exception("Formulas are invalid")

        self.mechanism_metadata.state = new_state


@dataclass
class Graph:
    nodes: dict[str, Node | None] = field(
        default_factory=lambda: {str(id): None for id in string.ascii_lowercase}
    )
    data: None = None

    def get_nodes(self) -> list[Node]:
        return [node for node in self.nodes.values() if node is not None]

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
        new_node.change_type("regression")

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
        if self._can_remove_edge(source, target) is False:
            raise Exception("Cannot remove edge")

        source.out_nodes.remove(target)
        target.in_nodes.remove(source)

    def _can_remove_edge(self, source: Node, target: Node) -> bool:
        source_removable = source.id_ in [n.id_ for n in target.in_nodes]
        target_removable = target.id_ in [n.id_ for n in source.out_nodes]
        return source_removable and target_removable

    def _get_generation_hierarchy(self) -> dict[int, set[str]]:
        all_nodes_ids = self.get_node_ids()
        hierarchy: dict[int, set[str]] = {}
        available_node_ids = set(
            [x.id_ for x in self.get_nodes() if len(x.get_in_node_ids()) == 0]
        )
        hierarchy[0] = available_node_ids
        current_layer = 1
        while len(available_node_ids) != len(all_nodes_ids):
            unassigned_node_ids = [
                x for x in all_nodes_ids if x not in available_node_ids
            ]
            next_layer_nodes = set()
            for x in unassigned_node_ids:
                node = self.get_node_by_id(x)
                assert node is not None
                in_nodes = set(node.get_in_node_ids())
                if in_nodes.intersection(available_node_ids) == in_nodes:
                    next_layer_nodes.add(x)
            hierarchy[current_layer] = next_layer_nodes
            current_layer += 1
            available_node_ids = available_node_ids.union(next_layer_nodes)
        return hierarchy

    def generate_full_data_set(self) -> pd.DataFrame:
        if not all(x.mechanism_metadata.state == "locked" for x in self.get_nodes()):
            raise Exception("All formulas need to be locked before generating data")

        hierarchy = self._get_generation_hierarchy()
        for layer in hierarchy.values():
            for node_id in layer:
                node = self.get_node_by_id(node_id)
                if node is None:
                    raise Exception(f"Failed to find node with id: {node_id}")

                inputs: dict[str, np.ndarray] = {
                    f"n_{node_id}": node.noise.generate_data()
                }

                for in_node_id in node.get_in_node_ids():
                    in_node = self.get_node_by_id(in_node_id)
                    if in_node is None or in_node.data is None:
                        raise Exception(f"Failed to find node with id: {in_node_id}")
                    inputs[in_node_id] = in_node.data

                formulas = [x for x in node.mechanism_metadata.get_formulas().values()]
                if len(formulas) < 1:
                    raise Exception("Invalid number of formulas found")

                match node.mechanism_metadata.mechanism_type:
                    case "classification":
                        mechanism = ClassificationMechanism(
                            formulas=formulas, inputs=inputs
                        )
                        result = mechanism.transform()
                        if result.error is not None:
                            raise Exception("Failed to evaluate")
                    case "regression":
                        mechanism = RegressionMechanism(
                            formulas=formulas, inputs=inputs
                        )
                        result = mechanism.transform()
                        if result.error is not None:
                            raise Exception("Failed to evaluate")

                assert result.values is not None
                node.data = result.values

        dataframe = pd.DataFrame.from_dict(
            {
                node_id: node.data
                for node_id, node in self.nodes.items()
                if node is not None
            }
        )
        if sorted(dataframe.columns.tolist()) != sorted(self.get_node_ids()):
            raise Exception("Inconsisten columns")

        return dataframe


# TODO: initial graph setup -> replace with imported settings if available
graph = Graph()
graph.add_node()
graph.add_node()
a = graph.get_node_by_id("a")
b = graph.get_node_by_id("b")
assert a is not None and b is not None, "Failed at init"
graph.add_edge(a, b)
