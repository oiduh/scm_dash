from unittest import TestCase
from models.graph import Graph, Node
import string


class GraphTest(TestCase):
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
        self.assertEqual(graph.get_node_by_id('a').id, 'a')
        self.assertEqual(graph.get_node_by_id('a').name, 'a')
        self.assertListEqual(graph.get_node_by_id('a').in_nodes, list())
        self.assertListEqual(graph.get_node_by_id('a').out_nodes, list())
        self.assertIsNotNone(graph.get_node_by_id('a').data)

        free_node = graph.get_free_node_id()
        assert free_node, "Could not find free node"
        self.assertEqual(free_node, 'b')

        self.assertListEqual(graph.get_node_ids(), ['a'])
        self.assertListEqual(graph.get_node_names(), ['a'])

        with self.assertRaises(Exception):
            graph.get_node_by_id('b')
        with self.assertRaises(Exception):
            graph.get_node_by_name('b')
        with self.assertRaises(Exception):
            graph.remove_node(Node('b', 'b', list(), list(), graph))
        
        mechanism = graph.get_node_by_id('a').mechanism
        valid_formula = mechanism.get_class_by_id('0')
        assert valid_formula
        self.assertTrue(valid_formula.enabled)
        invalid_formula = mechanism.get_class_by_id('1')
        assert invalid_formula
        self.assertFalse(invalid_formula.enabled)

        graph.remove_node(Node('a', 'a', list(), list(), graph))

        self.assertListEqual(graph.get_node_ids(), [])
        self.assertListEqual(graph.get_node_names(), [])

    def test_full_graph(self):
        graph = Graph()
        for _ in string.ascii_lowercase:
            graph.add_node()

        with self.assertRaises(Exception):
            graph.add_node()

        free_node = graph.get_free_node_id()
        self.assertIsNone(free_node)

        self.assertListEqual(graph.get_node_ids(), [x for x in string.ascii_lowercase])
        self.assertListEqual(graph.get_node_names(), [x for x in string.ascii_lowercase])

        for letter in string.ascii_lowercase:
            by_id = graph.get_node_by_id(letter)
            self.assertEqual(by_id.id, letter)
            by_name = graph.get_node_by_name(letter)
            self.assertEqual(by_name.name, letter)

        for letter in string.ascii_lowercase:
            graph.remove_node(Node(letter, letter, list(), list(), graph))

        self.assertListEqual(graph.get_node_ids(), [])
        self.assertListEqual(graph.get_node_names(), [])

    def test_add_and_remove_node(self):
        graph = Graph()

        graph.add_node()  # a
        graph.add_node()  # b
        graph.add_node()  # c

        self.assertListEqual(graph.get_node_ids(), ['a', 'b', 'c'])

        graph.remove_node(Node('a', 'a', list(), list(), graph))
        self.assertListEqual(graph.get_node_ids(), ['b', 'c'])

        graph.remove_node(Node('b', 'b', list(), list(), graph))
        self.assertListEqual(graph.get_node_ids(), ['c'])

        graph.add_node()
        self.assertListEqual(graph.get_node_ids(), ['a', 'c'])

    def test_graph_cyclic(self):
        graph = Graph()

        with self.assertRaises(Exception):
            graph.can_add_edge(
                Node('a', 'a', list(), list(), graph), Node('b', 'b', list(), list(), graph)
            )

        graph.add_node()  # a
        with self.assertRaises(Exception):
            graph.can_add_edge(
                graph.get_node_by_id('a'), Node('b', 'b', list(), list(), graph)
            )
        self.assertFalse(graph.can_add_edge(
            graph.get_node_by_id('a'), graph.get_node_by_id('a')
        ))

        graph.add_node()  # b
        self.assertTrue(graph.can_add_edge(
            graph.get_node_by_id('a'), graph.get_node_by_id('b')
        ))
        self.assertTrue(graph.can_add_edge(
            graph.get_node_by_id('b'), graph.get_node_by_id('a')
        ))
        self.assertFalse(graph.can_add_edge(
            graph.get_node_by_id('a'), graph.get_node_by_id('a')
        ))
        self.assertFalse(graph.can_add_edge(
            graph.get_node_by_id('b'), graph.get_node_by_id('b')
        ))

        graph.add_edge(
            graph.get_node_by_id('a'), graph.get_node_by_id('b')
        )

        self.assertIn('a', graph.get_node_by_id('b').get_in_node_ids())
        self.assertIn('b', graph.get_node_by_id('a').get_out_node_ids())
        self.assertFalse(graph.can_add_edge(
            graph.get_node_by_id('b'), graph.get_node_by_id('a')
        ))

        graph.add_node()  # c
        self.assertListEqual(graph.get_node_ids(), ['a', 'b', 'c'])
        self.assertTrue(graph.can_add_edge(
            graph.get_node_by_id('b'), graph.get_node_by_id('c')
        ))
        graph.add_edge(
            graph.get_node_by_id('b'), graph.get_node_by_id('c')
        )
        self.assertIn('b', graph.get_node_by_id('c').get_in_node_ids())
        self.assertIn('c', graph.get_node_by_id('b').get_out_node_ids())
        self.assertFalse(graph.can_add_edge(
            graph.get_node_by_id('c'), graph.get_node_by_id('a')
        ))
        self.assertTrue(graph.can_add_edge(
            graph.get_node_by_id('a'), graph.get_node_by_id('c')
        ))

        graph.add_edge(
            graph.get_node_by_id('a'), graph.get_node_by_id('c')
        )
        self.assertIn('a', graph.get_node_by_id('b').get_in_node_ids())
        self.assertIn('a', graph.get_node_by_id('c').get_in_node_ids())
        self.assertListEqual(['b', 'c'], graph.get_node_by_id('a').get_out_node_ids())

    def test_remove_edges(self):
        graph = Graph()

        graph.add_node()  # a
        graph.add_node()  # b
        graph.add_node()  # c

        graph.add_edge(graph.get_node_by_id('a'), graph.get_node_by_id('b'))
        graph.add_edge(graph.get_node_by_id('b'), graph.get_node_by_id('c'))
        graph.add_edge(graph.get_node_by_id('a'), graph.get_node_by_id('c'))

        self.assertListEqual([], graph.get_node_by_id('a').get_in_node_ids())
        self.assertListEqual(['a'], graph.get_node_by_id('b').get_in_node_ids())
        self.assertListEqual(['a', 'b'], sorted(graph.get_node_by_id('c').get_in_node_ids()))
        self.assertListEqual(['b', 'c'], sorted(graph.get_node_by_id('a').get_out_node_ids()))
        self.assertListEqual(['c'], sorted(graph.get_node_by_id('b').get_out_node_ids()))
        self.assertListEqual([], sorted(graph.get_node_by_id('c').get_out_node_ids()))

        graph.remove_node(graph.get_node_by_id('c'))  # destroy links: a->c, b->c
        with self.assertRaises(Exception):
            graph.get_node_by_id('c')
        self.assertListEqual([], graph.get_node_by_id('a').get_in_node_ids())
        self.assertListEqual(['a'], graph.get_node_by_id('b').get_in_node_ids())
        self.assertListEqual(['b'], sorted(graph.get_node_by_id('a').get_out_node_ids()))
        self.assertListEqual([], sorted(graph.get_node_by_id('b').get_out_node_ids()))

        graph.remove_edge(graph.get_node_by_id('a'), graph.get_node_by_id('b'))
        self.assertListEqual([], graph.get_node_by_id('a').get_in_node_ids())
        self.assertListEqual([], graph.get_node_by_id('b').get_in_node_ids())
        self.assertListEqual([], sorted(graph.get_node_by_id('a').get_out_node_ids()))
        self.assertListEqual([], sorted(graph.get_node_by_id('b').get_out_node_ids()))

        graph.add_node()
        graph.add_edge(graph.get_node_by_id('a'), graph.get_node_by_id('b'))
        graph.add_edge(graph.get_node_by_id('b'), graph.get_node_by_id('c'))
        graph.add_edge(graph.get_node_by_id('a'), graph.get_node_by_id('c'))
        self.assertListEqual([], graph.get_node_by_id('a').get_in_node_ids())
        self.assertListEqual(['a'], graph.get_node_by_id('b').get_in_node_ids())
        self.assertListEqual(['a', 'b'], sorted(graph.get_node_by_id('c').get_in_node_ids()))
        self.assertListEqual(['b', 'c'], sorted(graph.get_node_by_id('a').get_out_node_ids()))
        self.assertListEqual(['c'], sorted(graph.get_node_by_id('b').get_out_node_ids()))
        self.assertListEqual([], sorted(graph.get_node_by_id('c').get_out_node_ids()))

        graph.remove_node(graph.get_node_by_id('b'))
        self.assertListEqual([], graph.get_node_by_id('a').get_in_node_ids())
        self.assertListEqual(['a'], sorted(graph.get_node_by_id('c').get_in_node_ids()))
        self.assertListEqual(['c'], sorted(graph.get_node_by_id('a').get_out_node_ids()))
        self.assertListEqual([], sorted(graph.get_node_by_id('c').get_out_node_ids()))

