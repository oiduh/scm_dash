import string
from unittest import TestCase

from models.graph import Graph, Node


class GraphTest(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_empty_graph(self):
        graph = Graph()
        letters = set(char for char in string.ascii_lowercase)
        node_ids = set(graph.nodes.keys())
        self.assertSetEqual(letters, node_ids)
        for node in graph.nodes.values():
            self.assertIsNone(node)

    def test_one_node(self):
        graph = Graph()
        graph.add_node()

        node = graph.get_node_by_id("a")
        assert node is not None

        self.assertEqual(node.id_, "a")
        self.assertEqual(node.name, "a")
        self.assertListEqual(node.in_nodes, list())
        self.assertListEqual(node.out_nodes, list())
        self.assertIsNotNone(node.noise)

        free_node = graph.get_free_node_id()
        assert free_node is not None
        self.assertEqual(free_node, "b")

        self.assertListEqual(graph.get_node_ids(), ["a"])
        self.assertListEqual(graph.get_node_names(), ["a"])
        self.assertIsNone(graph.get_node_by_id("b"))
        self.assertIsNone(graph.get_node_by_name("b"))

        with self.assertRaises(Exception):
            graph.remove_node(Node("b", "b", graph))

        mechanism = node.mechanism_metadata
        valid_formula = mechanism.get_class_by_id("0")
        assert valid_formula is not None

        invalid_formula = mechanism.get_class_by_id("1")
        assert invalid_formula is None

        graph.remove_node(Node("a", "a", graph))

        self.assertListEqual(graph.get_node_ids(), [])
        self.assertListEqual(graph.get_node_names(), [])

    def test_full_graph(self):
        graph = Graph()
        # can add only ascii lowercase chars as ids
        for _ in string.ascii_lowercase:
            graph.add_node()

        with self.assertRaises(Exception):
            graph.add_node()

        free_node = graph.get_free_node_id()
        assert free_node is None

        self.assertListEqual(graph.get_node_ids(), [x for x in string.ascii_lowercase])
        self.assertListEqual(
            graph.get_node_names(), [x for x in string.ascii_lowercase]
        )

        for letter in string.ascii_lowercase:
            by_id = graph.get_node_by_id(letter)
            assert by_id is not None
            self.assertEqual(by_id.id_, letter)
            by_name = graph.get_node_by_name(letter)
            assert by_name is not None
            self.assertEqual(by_name.name, letter)

        for letter in string.ascii_lowercase:
            graph.remove_node(Node(letter, letter, graph))

        self.assertListEqual(graph.get_node_ids(), [])
        self.assertListEqual(graph.get_node_names(), [])

    def test_add_and_remove_node(self):
        graph = Graph()

        graph.add_node()  # a
        graph.add_node()  # b
        graph.add_node()  # c

        self.assertListEqual(graph.get_node_ids(), ["a", "b", "c"])

        graph.remove_node(Node("a", "a", graph))
        self.assertListEqual(graph.get_node_ids(), ["b", "c"])

        graph.remove_node(Node("b", "b", graph))
        self.assertListEqual(graph.get_node_ids(), ["c"])

        graph.add_node()
        self.assertListEqual(graph.get_node_ids(), ["a", "c"])

    def test_graph_cyclic(self):
        graph = Graph()

        with self.assertRaises(Exception):
            graph.can_add_edge(
                Node("a", "a", graph),
                Node("b", "b", graph),
            )

        graph.add_node()  # a
        node_a = graph.get_node_by_id("a")
        assert node_a is not None
        with self.assertRaises(Exception):
            graph.can_add_edge(node_a, Node("b", "b", graph))
        self.assertFalse(graph.can_add_edge(node_a, node_a))

        graph.add_node()  # b
        node_b = graph.get_node_by_id("b")
        assert node_b is not None
        self.assertTrue(graph.can_add_edge(node_a, node_b))
        self.assertTrue(graph.can_add_edge(node_b, node_a))
        self.assertFalse(graph.can_add_edge(node_a, node_a))
        self.assertFalse(graph.can_add_edge(node_b, node_b))

        graph.add_edge(node_a, node_b)

        self.assertIn("a", node_b.get_in_node_ids())
        self.assertIn("b", node_a.get_out_node_ids())
        self.assertFalse(graph.can_add_edge(node_b, node_a))

        graph.add_node()  # c
        node_c = graph.get_node_by_id("c")
        assert node_c is not None
        self.assertListEqual(graph.get_node_ids(), ["a", "b", "c"])
        self.assertTrue(graph.can_add_edge(node_b, node_c))
        graph.add_edge(node_b, node_c)
        self.assertIn("b", node_c.get_in_node_ids())
        self.assertIn("c", node_b.get_out_node_ids())
        self.assertFalse(graph.can_add_edge(node_c, node_a))
        self.assertTrue(graph.can_add_edge(node_a, node_c))

        graph.add_edge(node_a, node_c)
        self.assertIn("a", node_b.get_in_node_ids())
        self.assertIn("a", node_c.get_in_node_ids())
        self.assertListEqual(["b", "c"], node_a.get_out_node_ids())

    def test_remove_edges(self):
        graph = Graph()

        graph.add_node()  # a
        graph.add_node()  # b
        graph.add_node()  # c

        node_a = graph.get_node_by_id("a")
        assert node_a is not None
        node_b = graph.get_node_by_id("b")
        assert node_b is not None
        node_c = graph.get_node_by_id("c")
        assert node_c is not None

        # no cycles
        graph.add_edge(node_a, node_b)
        graph.add_edge(node_b, node_c)
        graph.add_edge(node_a, node_c)

        self.assertListEqual([], node_a.get_in_node_ids())
        self.assertListEqual(["a"], node_b.get_in_node_ids())
        self.assertListEqual(["a", "b"], sorted(node_c.get_in_node_ids()))
        self.assertListEqual(["b", "c"], sorted(node_a.get_out_node_ids()))
        self.assertListEqual(["c"], sorted(node_b.get_out_node_ids()))
        self.assertListEqual([], sorted(node_c.get_out_node_ids()))

        graph.remove_node(node_c)  # destroy links: a->c, b->c
        self.assertIsNone(graph.get_node_by_id("c"))
        self.assertListEqual([], node_a.get_in_node_ids())
        self.assertListEqual(["a"], node_b.get_in_node_ids())
        self.assertListEqual(["b"], sorted(node_a.get_out_node_ids()))
        self.assertListEqual([], sorted(node_b.get_out_node_ids()))

        graph.remove_edge(node_a, node_b)
        self.assertListEqual([], node_a.get_in_node_ids())
        self.assertListEqual([], node_b.get_in_node_ids())
        self.assertListEqual([], sorted(node_a.get_out_node_ids()))
        self.assertListEqual([], sorted(node_b.get_out_node_ids()))

        graph.add_node()  # re-add c
        node_c = graph.get_node_by_id("c")
        assert node_c is not None
        graph.add_edge(node_a, node_b)
        graph.add_edge(node_b, node_c)
        graph.add_edge(node_a, node_c)
        self.assertListEqual([], node_a.get_in_node_ids())
        self.assertListEqual(["a"], node_b.get_in_node_ids())
        self.assertListEqual(["a", "b"], sorted(node_c.get_in_node_ids()))
        self.assertListEqual(["b", "c"], sorted(node_a.get_out_node_ids()))
        self.assertListEqual(["c"], sorted(node_b.get_out_node_ids()))
        self.assertListEqual([], sorted(node_c.get_out_node_ids()))

        graph.remove_node(node_b)
        self.assertListEqual([], node_a.get_in_node_ids())
        self.assertListEqual(["a"], sorted(node_c.get_in_node_ids()))
        self.assertListEqual(["c"], sorted(node_a.get_out_node_ids()))
        self.assertListEqual([], sorted(node_c.get_out_node_ids()))
