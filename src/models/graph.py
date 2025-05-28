import string
from copy import deepcopy
from dataclasses import dataclass, field
import json
from typing import Any, Self

import numpy as np
import pandas as pd

from models.mechanism import (
    ClassificationMechanism,
    MechanismMetadata,
    MechanismResult,
    MechanismState,
    MechanismType,
    RegressionMechanism,
)
from models.noise import Noise


@dataclass
class Node:
    id_: str

    name: str | None = None
    in_nodes: list[str] = field(default_factory=list)
    out_nodes: list[str] = field(default_factory=list)
    noise: Noise = field(init=False)
    data: np.ndarray | None = None
    mechanism_metadata: MechanismMetadata = field(init=False)

    def __post_init__(self) -> None:
        self.noise = Noise.default_noise()
        self.mechanism_metadata = MechanismMetadata()

    def add_in_node(self, to_add: Self) -> None:
        """
        Exception:
            target node already an in node
        """
        if to_add.id_ in self.in_nodes:
            raise Exception("Node already an in_node")
        self.in_nodes.append(to_add.id_)

    def add_out_node(self, to_add: Self) -> None:
        """
        Exception:
            target node already an out node
        """
        if to_add.id_ in self.out_nodes:
            raise Exception("Node already an out_node")
        self.out_nodes.append(to_add.id_)

    def remove_in_node(self, to_remove: Self) -> None:
        """
        Exception:
            target node not an in node
        """
        if to_remove.id_ not in self.in_nodes:
            raise Exception("Target node is not an in node")
        self.in_nodes.remove(to_remove.id_)

    def remove_out_node(self, to_remove: Self) -> None:
        """
        Exception:
            target node not an out node
        """
        if to_remove.id_ not in self.out_nodes:
            raise Exception("Target node is not an out node")
        self.out_nodes.remove(to_remove.id_)

    def change_type(self, new_type: MechanismType) -> None:
        self.mechanism_metadata.mechanism_type = new_type
        self.mechanism_metadata.reset_formulas()

    def formulas_are_valid(self) -> MechanismResult:
        # data in range (-5.0, 5.0)
        # just a sanity check, values might not be correct for actual outcome
        input_ids = []
        input_ids.append(f"n_{self.name or self.id_}")  # add noise to inputs as well
        input_ids.extend([w.name or w.id_ for w in [graph.get_node_by_id(z) for z in self.in_nodes] if w is not None])
        data = {node_id: (np.random.rand(1000) - 0.5) * 10 for node_id in input_ids}
        formulas = list(self.mechanism_metadata.get_formulas().values())

        match self.mechanism_metadata.mechanism_type:
            case "regression":
                mechanism = RegressionMechanism(formulas, data)
            case "classification":
                mechanism = ClassificationMechanism(formulas, data)

        # we do not care about the data, only if the data generation failed e.g. invalid values
        # its just a data generation trial to check for basic errors, might be a false positive
        mechanism_result = mechanism.transform()
        self.mechanism_metadata.valid = mechanism_result.error is None
        return mechanism_result

    @classmethod
    def parse_from_dict(cls, node_id: str, node_dict: dict[str, Any]) -> Self:
        new_node = cls(node_id)

        name = node_dict.get("name")
        if name is None:
            new_node.name = node_id
        elif isinstance(name, str):
            assert len(name) > 1 and name[0] in string.ascii_letters, (
                "invalid name 1"
            )
            new_node.name = name
        else:
            assert False, "invalid name 2"

        assert (in_nodes := node_dict.get("in_nodes")) is not None and isinstance(in_nodes, list), (
            "invalid in_nodes 1"
        )
        assert len(in_nodes) == 0 or all(isinstance(e, str) and len(e) == 1 for e in in_nodes), (
            "invalid in_nodes 2"
        )
        assert len(in_nodes) == len(set(in_nodes)), (
            "invalid in_nodes 3"
        )
        new_node.in_nodes = in_nodes

        assert (out_nodes := node_dict.get("out_nodes")) is not None and isinstance(out_nodes, list), (
            "invalid out_nodes 1"
        )
        assert len(out_nodes) == 0 or all(isinstance(e, str) and len(e) == 1 for e in out_nodes), (
            "invalid out_nodes 1"
        )
        assert len(out_nodes) == len(set(out_nodes)), (
            "invalid out_nodes 1"
        )
        new_node.out_nodes = out_nodes

        assert (noise_data := node_dict.get("noise")) is not None and isinstance(noise_data, dict), (
            "noise data dict error"
        )
        new_node.noise = Noise.parse_from_dict(noise_data)

        assert (mechanism_data := node_dict.get("mechanism")) is not None and isinstance(mechanism_data, dict), (
            "mechanism data dict error"
        )
        new_node.mechanism_metadata = MechanismMetadata.parse_from_dict(mechanism_data)

        return new_node



@dataclass
class Graph:
    nodes: dict[str, Node | None] = field(
        default_factory=lambda: {str(id): None for id in string.ascii_lowercase}
    )
    data: pd.DataFrame | None = None
    data_sets: list[dict[str, str | list[str]]] = field(default_factory=list)
    # TODO:add support for intervention for data sets field e.g. bool and int accepted

    def get_nodes(self) -> list[Node]:
        return [node for node in self.nodes.values() if node is not None]

    def get_node_ids(self) -> list[str]:
        return [node.id_ for node in self.get_nodes()]

    def get_node_names(self) -> list[str]:
        return [node.name for node in self.get_nodes() if node.name is not None]

    def get_node_by_id(self, id_: str) -> Node | None:
        return self.nodes.get(id_)

    def get_node_by_name(self, name: str) -> Node | None:
        nodes = (node for node in self.get_nodes() if node.name == name)
        return next(nodes, None)

    def get_free_node_id(self) -> str | None:
        free_node_ids = (id for id, node in self.nodes.items() if node is None)
        return next(free_node_ids, None)

    def add_node(self) -> str:
        free_node_id = self.get_free_node_id()
        if free_node_id is None:
            raise Exception("Cannot add another node")

        new_node = Node(free_node_id, free_node_id)
        self.nodes[free_node_id] = new_node
        new_node.change_type("regression")
        return new_node.id_

    def remove_node(self, to_remove: Node) -> None:
        """
        Exception:
            node does not exist
        """
        if self.nodes.get(to_remove.id_) is None:
            raise Exception("Node does not exist")

        for node in self.get_nodes():
            if to_remove.id_ in node.in_nodes:
                node.remove_in_node(to_remove)
            if to_remove.id_ in node.out_nodes:
                node.remove_out_node(to_remove)

        self.nodes[to_remove.id_] = None

    def add_edge(self, source: Node, target: Node) -> None:
        if self.can_add_edge(source, target) is False:
            raise Exception("Cannot add edge")

        source.add_out_node(target)
        target.add_in_node(source)

    def can_add_edge(self, source: Node, target: Node) -> bool:
        print(f"checking {source.id_} -> {target.id_}")
        if source.id_ == target.id_:
            return False
        if source.id_ in target.in_nodes or source.id_ in target.out_nodes:
            return False

        graph_cpy = deepcopy(self)
        new_source = graph_cpy.get_node_by_id(source.id_)
        new_target = graph_cpy.get_node_by_id(target.id_)
        assert new_source is not None and new_target is not None
        new_source.add_out_node(new_target)
        new_target.add_in_node(new_source)

        return not Graph.is_cyclic(graph_cpy)

    @staticmethod
    def is_cyclic(graph_cpy: "Graph") -> bool:
        nodes_ids = graph_cpy.get_node_ids()
        visited = {k: False for k in nodes_ids}
        recursive_stack = {k: False for k in nodes_ids}

        for node_id in nodes_ids:
            if visited[node_id] is False:
                if Graph.is_cyclic_util(node_id, visited, recursive_stack, graph_cpy):
                    return True
        return False

    @staticmethod
    def is_cyclic_util(
        node_id: str,
        visited: dict[str, bool],
        recursive_stack: dict[str, bool],
        graph_cpy: "Graph",
    ) -> bool:
        visited[node_id] = True
        recursive_stack[node_id] = True
        node = graph.get_node_by_id(node_id)
        assert node is not None
        for neighbor in node.out_nodes:
            if not visited[neighbor]:
                if Graph.is_cyclic_util(neighbor, visited, recursive_stack, graph_cpy):
                    print("CYCLE 1")
                    return True
            elif recursive_stack[neighbor]:
                print("CYCLE 2")
                return True
        recursive_stack[node_id] = False
        return False

    def remove_edge(self, source: Node, target: Node) -> None:
        """
        Exception:
            edge cannot be removed
        """
        if self._can_remove_edge(source, target) is False:
            raise Exception("Cannot remove edge")

        source.out_nodes.remove(target.id_)
        target.in_nodes.remove(source.id_)

    def _can_remove_edge(self, source: Node, target: Node) -> bool:
        source_removable = source.id_ in target.in_nodes
        target_removable = target.id_ in source.out_nodes
        return source_removable and target_removable

    def _get_generation_hierarchy(self) -> dict[int, set[str]]:
        all_nodes_ids = self.get_node_ids()
        hierarchy: dict[int, set[str]] = {}
        available_node_ids = set(
            [x.id_ for x in self.get_nodes() if len(x.in_nodes) == 0]
        )
        hierarchy[0] = available_node_ids
        current_layer = 1


        print(f"{available_node_ids=}")
        print(f"{all_nodes_ids=}")
        for node in self.get_nodes():
            print(node.id_, node.in_nodes, node.out_nodes)


        while len(available_node_ids) != len(all_nodes_ids):
            # TODO: why infinite loop
            unassigned_node_ids = [
                x for x in all_nodes_ids if x not in available_node_ids
            ]
            next_layer_nodes = set()
            for x in unassigned_node_ids:
                node = self.get_node_by_id(x)
                assert node is not None
                in_nodes = set(node.in_nodes)
                if in_nodes.intersection(available_node_ids) == in_nodes:
                    next_layer_nodes.add(x)
            hierarchy[current_layer] = next_layer_nodes
            current_layer += 1
            available_node_ids = available_node_ids.union(next_layer_nodes)
        return hierarchy

    def generate_full_data_set(self) -> pd.DataFrame:
        hierarchy = self._get_generation_hierarchy()
        for layer in hierarchy.values():
            for node_id in layer:
                node = self.get_node_by_id(node_id)
                if node is None:
                    raise Exception(f"Failed to find node with id: {node_id}")

                inputs: dict[str, np.ndarray] = {
                    f"n_{node_id}": np.array(list(node.noise.generate_data().values())).flatten()
                }

                for in_node_id in node.in_nodes:
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
                    case _:
                        raise Exception("no mechanism type found")

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

    def add_data_set(self, sources: dict[str, bool], target: str) -> bool:
        node = self.get_node_by_id(target)
        assert node is not None, "there must be a node"
        sources_list = [k for k, v in sources.items() if v]
        new_data_set: dict[str, str | list[str]] = {
            "s": sources_list, "t": target, "m": node.mechanism_metadata.mechanism_type,
        }
        if new_data_set in self.data_sets:
            return False
        self.data_sets.append(new_data_set)
        return True

    def to_dict(self) -> str:
        # TODO: add source and target info to graph as well?
        graph_as_dict = {}
        for id_, node in self.nodes.items():
            if node is None:
                continue
            graph_as_dict[id_] = {}
            graph_as_dict[id_]["name"] = node.name if node.name != node.id_ else None
            graph_as_dict[id_]["in_nodes"] = node.in_nodes
            graph_as_dict[id_]["out_nodes"] = node.out_nodes
            graph_as_dict[id_]["noise"] = {}
            for distr_id, distr in node.noise.sub_distributions.items():
                if distr is None:
                    continue
                graph_as_dict[id_]["noise"][distr_id] = {
                    "name": distr.name,
                    "params": {}
                }
                for param_id, param in distr.parameters.items():
                    graph_as_dict[id_]["noise"][distr_id]["params"][param_id] = param.current
            graph_as_dict[id_]["mechanism"] = {
                "type": node.mechanism_metadata.mechanism_type,
                "formulas": {},
            }
            for mechanism_id, formula in node.mechanism_metadata.formulas.items():
                if formula is None:
                    continue
                graph_as_dict[id_]["mechanism"]["formulas"][mechanism_id] = formula

        if len(self.data_sets) > 0:
            graph_as_dict["data_sets"] = deepcopy(self.data_sets)

        return json.dumps(graph_as_dict)

    @staticmethod
    def verify_data_sets(target_graph: "Graph", data_sets: list[dict[str, list[str]]]) -> bool:
        hashable_data_sets: list[str] = []
        for data_set in data_sets:
            sources, target = data_set.get("s"), data_set.get("t")
            if not isinstance(sources, list):
                return False
            if not isinstance(target, str):
                return False

            # verify target
            if target not in target_graph.get_node_ids():
                return False

            # verify effects
            if len(sources) != len(set(sources)):
                return False
            if len(sources) == 0 or len(sources) >= len(target_graph.get_node_ids()):
                return False
            if target in sources:
                return False
            for source in sources:
                if source not in target_graph.get_node_ids():
                    return False

            hashable_data_sets.append(str(target) + "".join(sources))

        if len(hashable_data_sets) != len(set(hashable_data_sets)):
            return False

        return True



    @classmethod
    def parse_from_dict(cls, graph_data: dict[str, Any]) -> Self:
        graph_cpy = cls()
        data_sets = graph_data.get("data_sets")
        if data_sets is not None:
            del graph_data["data_sets"]

        # ids valid
        ids_ = list(graph_data.keys())
        assert all(isinstance(id_, str) and id_ in string.ascii_lowercase for id_ in ids_), (
            "wrong ids in graph"
        )
        assert all(isinstance(d, dict) for d in graph_data.values()), (
            "nodes not dicts"
        )
        for id_, d_ in graph_data.items():
            new_node = Node.parse_from_dict(id_, d_)
            graph_cpy.nodes[id_] = new_node

        # TODO: not sure if verification is needed
        if data_sets is not None:
            if not Graph.verify_data_sets(graph_cpy, data_sets):
                assert False, "data sets not valid"
            graph_cpy.data_sets = deepcopy(data_sets)

        return graph_cpy


# TODO: initial graph setup -> replace with imported settings if available
graph = Graph()
graph.add_node()
graph.add_node()
a = graph.get_node_by_id("a")
b = graph.get_node_by_id("b")
assert a is not None and b is not None, "Failed at init"
graph.add_edge(a, b)

new_graph: Graph | None = None
