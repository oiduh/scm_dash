import unittest
from unittest import TestCase

import numpy as np
import numpy.testing as npt

from models.graph import Graph
from models.mechanism import ClassificationMechanism, RegressionMechanism


class RegresionMechanismTest(TestCase):
    def test_simple_regression_mechanism(self):
        formulas = ["a + c*2 + 2"]
        inputs = [
            {"a": [-1.0, 2.0], "c": [2.0, -3.0]},
            {"a": [0.0, 0.0], "c": [0.0, 0.0]},
            {"a": [1.5, -2.2], "c": [-3.2, 0.1]},
        ]
        expecteds = [
            [5.0, -2.0],
            [2.0, 2.0],
            [-2.9, 0.0],
        ]
        for input, expected in zip(inputs, expecteds):
            regression = RegressionMechanism(formulas, input)
            result = regression.transform()
            assert result.error is None
            assert result.values is not None
            npt.assert_almost_equal(
                result.values, np.array(expected, dtype=np.float64), decimal=5
            )

    def test_complex_regression_mechanism(self):
        formulas = ["a**3 + (b-0.5)*2 - (c**2) + 1"]
        inputs = [
            {"a": [-1.0, 2.0], "b": [-2.0, -3.0], "c": [3.0, -3.0]},
            {"a": [0.0, 0.0], "b": [0.0, 0.0], "c": [0.0, 0.0]},
            {"a": [1.5, -2.2], "b": [3.9, -1.2], "c": [-3.2, 0.1]},
        ]
        expecteds = [
            [-14.0, -7.0],
            [0.0, 0.0],
            [0.935, -13.058],
        ]
        for input, expected in zip(inputs, expecteds):
            regression = RegressionMechanism(formulas, input)
            result = regression.transform()
            assert result.error is None
            assert result.values is not None
            npt.assert_almost_equal(
                result.values, np.array(expected, dtype=np.float128), decimal=5
            )

    def test_simple_regression_mechanism_long(self):
        formulas = ["(a**3)*0.1 + (b+1.3)*2.6 + 1"]
        inputs = [
            {
                "a": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
                "b": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 0.0],
            },
            {
                "a": [9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0],
                "b": [5.0, 4.0, 3.0, 2.0, 1.0, 0.0, 9.0, 8.0, 7.0, 6.0],
            },
        ]
        expecteds = [
            [6.98, 9.68, 12.98, 17.48, 23.78, 32.48, 44.18, 59.48, 78.98, 77.28],
            [90.28, 65.98, 46.48, 31.18, 19.48, 10.78, 30.48, 25.98, 22.68, 19.98],
        ]
        for input, expected in zip(inputs, expecteds):
            regression = RegressionMechanism(formulas, input)
            result = regression.transform()
            assert result.error is None
            assert result.values is not None
            npt.assert_almost_equal(
                result.values, np.array(expected, dtype=np.float128), decimal=5
            )

    def test_simple_regression_mechanism_builtin(self):
        formulas = ["sin(a) + exp(b) - sqrt(abs(c)) + arctan(d) + 1"]
        inputs = [
            {"a": [-1.0, 2.0], "b": [-2.0, -3.0], "c": [3.0, -3.0], "d": [3.0, -3.0]},
            {"a": [1.5, -2.2], "b": [3.9, -1.2], "c": [-3.2, 0.1], "d": [-3.2, 0.1]},
        ]
        expecteds = [
            [-0.18914, -1.02201],
            [48.34318, 0.27614],
        ]
        for input, expected in zip(inputs, expecteds):
            regression = RegressionMechanism(formulas, input)
            result = regression.transform()
            assert result.error is None
            assert result.values is not None
            npt.assert_almost_equal(
                result.values, np.array(expected, dtype=np.float128), decimal=5
            )

    def test_graph_mechanism(self):
        graph = Graph()
        graph.add_node()  # a
        graph.add_node()  # b
        graph.add_node()  # c

        a = graph.get_node_by_id("a")
        assert a is not None
        b = graph.get_node_by_id("b")
        assert b is not None
        c = graph.get_node_by_id("c")
        assert c is not None

        graph.add_edge(a, b)
        graph.add_edge(c, b)

        distr_0 = a.noise.get_distribution_by_id("0")
        assert distr_0 is not None
        param_loc = distr_0.get_parameter_by_name("loc")
        assert param_loc is not None
        param_loc.change_current(-2.0)

        a.noise.add_distribution()
        distr_1 = a.noise.get_distribution_by_id("1")
        assert distr_1 is not None
        param_loc = distr_1.get_parameter_by_name("loc")
        assert param_loc is not None
        param_loc.change_current(2.0)

        c.noise.add_distribution()
        distr_0 = c.noise.get_distribution_by_id("0")
        assert distr_0 is not None
        param_loc = distr_0.get_parameter_by_name("loc")
        assert param_loc is not None
        param_loc.change_current(-4.0)
        param_loc = distr_1.get_parameter_by_name("loc")
        assert param_loc is not None
        param_loc.change_current(4.0)

        formulas = ["sin(a) + cos(3.2+a)*c"]
        b_in_nodes_ids = b.get_in_node_ids()
        b_in_nodes = [graph.get_node_by_id(x) for x in b_in_nodes_ids]
        inputs = {
            node.id_: node.noise.generate_data().tolist()
            for node in b_in_nodes
            if node is not None
        }
        self.assertSetEqual(set(inputs.keys()), {"a", "c"})
        regression = RegressionMechanism(formulas, inputs)
        result = regression.transform()
        assert result.error is None
        assert result.values is not None
        self.assertEqual(result.values.shape, (3000,))
        self.assertTrue(all(np.isfinite(result.values)))


class ClassficationMechanismTest(TestCase):
    def test_simple_classification_mechanism(self):
        formulas = ["a > 0.0"]
        inputs = [
            {
                "a": [-1.0, 2.0],
            },
            {
                "a": [2.0, -1.0],
            },
            {
                "a": [0.0, 0.0],
            },
            {
                "a": [1.5, 2.2],
            },
        ]
        expecteds = [
            [[False, True], [True, False]],
            [[True, False], [False, True]],
            [[False, False], [True, True]],
            [[True, True], [False, False]],
        ]

        for input, expected in zip(inputs, expecteds):
            classification = ClassificationMechanism(formulas, input)
            result = classification.transform()
            assert result.error is None
            assert result.values is not None
            self.assertListEqual(result.values.tolist(), expected)

    def test_complex_classification_mechanism(self):
        formulas = ["(a > 0.0) & ((abs(ceil(b)) < 1.0))"]
        inputs = [
            {"a": [-1.0, 2.0], "b": [-0.8, -0.1]},
            {"a": [1.0, 2.0], "b": [-0.8, -1.1]},
            {"a": [-1.0, 2.0], "b": [-0.8, -1.1]},
            {"a": [1.0, 2.0], "b": [-0.8, -0.9]},
        ]
        expecteds = [
            [[False, True], [True, False]],
            [[True, False], [False, True]],
            [[False, False], [True, True]],
            [[True, True], [False, False]],
        ]

        for input, expected in zip(inputs, expecteds):
            classification = ClassificationMechanism(formulas, input)
            result = classification.transform()
            assert result.error is None
            assert result.values is not None
            self.assertListEqual(result.values.tolist(), expected)

    def test_simple_classification_mechanism_multi_class(self):
        formulas = ["(a > 2.0) | (a < -2.0)", "(a > -0.5) & (a < 0.5)"]
        inputs = [
            {
                "a": [5.0, 0.0, 1.0],
            },
            {
                "a": [0.0, 5.0, 1.0],
            },
            {
                "a": [0.0, 0.0, 0.0],
            },
            {
                "a": [5.0, -5.0, 5.0],
            },
            {
                "a": [1.0, -1.0, 1.0],
            },
        ]
        expecteds = [
            [[True, False, False], [False, True, False], [False, False, True]],
            [[False, True, False], [True, False, False], [False, False, True]],
            [[False, False, False], [True, True, True], [False, False, False]],
            [[True, True, True], [False, False, False], [False, False, False]],
            [[False, False, False], [False, False, False], [True, True, True]],
        ]

        for input, expected in zip(inputs, expecteds):
            classification = ClassificationMechanism(formulas, input)
            result = classification.transform()
            assert result.error is None
            assert result.values is not None
            self.assertListEqual(result.values.tolist(), expected)

    def test_complex_classification_mechanism_multi_class(self):
        formulas = ["(a > 2.0) & (b > 2.0)", "(a < -2.0) & (b < -2.0)"]
        inputs = [
            {
                "a": [5.0, -5.0, 0.0],
                "b": [5.0, -5.0, 0.0],
            },
            {
                "a": [-5.0, 5.0, 0.0],
                "b": [-5.0, 5.0, 0.0],
            },
            {
                "a": [-5.0, 5.0, 0.0],
                "b": [5.0, -5.0, 0.0],
            },
        ]
        expecteds = [
            [[True, False, False], [False, True, False], [False, False, True]],
            [[False, True, False], [True, False, False], [False, False, True]],
            [[False, False, False], [False, False, False], [True, True, True]],
        ]

        for input, expected in zip(inputs, expecteds):
            classification = ClassificationMechanism(formulas, input)
            result = classification.transform()
            assert result.error is None
            assert result.values is not None
            self.assertListEqual(result.values.tolist(), expected)

    def test_graph_mechanism(self):
        graph = Graph()
        graph.add_node()  # a
        graph.add_node()  # b
        graph.add_node()  # c

        a = graph.get_node_by_id("a")
        assert a is not None
        b = graph.get_node_by_id("b")
        assert b is not None
        c = graph.get_node_by_id("c")
        assert c is not None

        graph.add_edge(a, b)
        graph.add_edge(c, b)

        distr_0 = a.noise.get_distribution_by_id("0")
        assert distr_0 is not None
        param_loc = distr_0.get_parameter_by_name("loc")
        assert param_loc is not None
        param_loc.change_current(-2.0)

        a.noise.add_distribution()
        distr_1 = a.noise.get_distribution_by_id("1")
        assert distr_1 is not None
        param_loc = distr_1.get_parameter_by_name("loc")
        assert param_loc is not None
        param_loc.change_current(2.0)

        distr_0 = c.noise.get_distribution_by_id("0")
        assert distr_0 is not None
        param_loc = distr_0.get_parameter_by_name("loc")
        assert param_loc is not None
        param_loc.change_current(-4.0)

        c.noise.add_distribution()
        distr_1 = c.noise.get_distribution_by_id("1")
        assert distr_1 is not None
        param_loc = distr_1.get_parameter_by_name("loc")
        assert param_loc is not None
        param_loc.change_current(4.0)

        formulas = ["(a > 2.0) & (c > 4.0)", "(a < -2.0) & (c < -4.0)"]
        b_in_nodes_ids = b.get_in_node_ids()
        b_in_nodes = [graph.get_node_by_id(x) for x in b_in_nodes_ids]
        inputs = {
            node.id_: node.noise.generate_data().tolist()
            for node in b_in_nodes
            if node is not None
        }
        self.assertSetEqual(set(inputs.keys()), {"a", "c"})
        classifcation = ClassificationMechanism(formulas, inputs)
        result = classifcation.transform()
        assert result.error is None
        assert result.values is not None
        self.assertEqual(result.values.shape, (3, 3000))
