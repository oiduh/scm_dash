from unittest import TestCase
import unittest
import numpy.testing as npt
import numpy as np
from models.graph import Graph
from models.mechanism import RegressionMechanism, ClassificationMechanism


class RegresionMechanismTest(TestCase):
    def test_simple_regression_mechanism(self):
        formulas = ["a + c*2 + 2"]
        inputs = [
            {
                "a": [-1., 2.],
                "c": [2., -3.]
            },
            {
                "a": [0., 0.],
                "c": [0., 0.]
            },
            {
                "a": [1.5, -2.2],
                "c": [-3.2, 0.1]
            }
        ]
        expecteds = [
            [5.0, -2.0],
            [2.0, 2.0],
            [-2.9, 0.0],
        ]
        for input, expected in zip(inputs, expecteds):
            regression = RegressionMechanism(formulas, input)
            result = regression.transform()
            npt.assert_almost_equal(result, np.array(expected, dtype=np.float128), decimal=5)

    def test_complex_regression_mechanism(self):
        formulas = ["a**3 + (b-0.5)*2 - (c**2) + 1"]
        inputs = [
            {
                "a": [-1., 2.],
                "b": [-2., -3.],
                "c": [3., -3.]
            },
            {
                "a": [0., 0.],
                "b": [0., 0.],
                "c": [0., 0.]
            },
            {
                "a": [1.5, -2.2],
                "b": [3.9, -1.2],
                "c": [-3.2, 0.1]
            }
        ]
        expecteds = [
            [-14., -7.],
            [0.0, 0.0],
            [0.935, -13.058],
        ]
        for input, expected in zip(inputs, expecteds):
            regression = RegressionMechanism(formulas, input)
            result = regression.transform()
            npt.assert_almost_equal(result, np.array(expected, dtype=np.float128), decimal=5)

    def test_simple_regression_mechanism_long(self):
        formulas = ["(a**3)*0.1 + (b+1.3)*2.6 + 1"]
        inputs = [
            {
                "a": [0., 1., 2., 3., 4., 5., 6., 7., 8., 9.],
                "b": [1., 2., 3., 4., 5., 6., 7., 8., 9., 0.],
            },
            {
                "a": [9., 8., 7., 6., 5., 4., 3., 2., 1., 0.],
                "b": [5., 4., 3., 2., 1., 0., 9., 8., 7., 6.],
            },
        ]
        expecteds = [
            [6.98, 9.68, 12.98, 17.48, 23.78, 32.48, 44.18, 59.48, 78.98, 77.28],
            [90.28, 65.98, 46.48, 31.18, 19.48, 10.78, 30.48, 25.98, 22.68, 19.98],
        ]
        for input, expected in zip(inputs, expecteds):
            regression = RegressionMechanism(formulas, input)
            result = regression.transform()
            npt.assert_almost_equal(result, np.array(expected, dtype=np.float128), decimal=5)

    def test_simple_regression_mechanism_builtin(self):
        formulas = ["sin(a) + exp(b) - sqrt(abs(c)) + arctan(d) + 1"]
        inputs = [
            {
                "a": [-1., 2.],
                "b": [-2., -3.],
                "c": [3., -3.],
                "d": [3., -3.]
            },
            {
                "a": [1.5, -2.2],
                "b": [3.9, -1.2],
                "c": [-3.2, 0.1],
                "d": [-3.2, 0.1]
            }
        ]
        expecteds = [
            [-0.18914, -1.02201],
            [48.34318, 0.27614],
        ]
        for input, expected in zip(inputs, expecteds):
            regression = RegressionMechanism(formulas, input)
            result = regression.transform()
            npt.assert_almost_equal(result, np.array(expected, dtype=np.float128), decimal=5)


    def test_graph_mechanism(self):
        graph = Graph()
        graph.add_node()  # a
        graph.add_node()  # b
        graph.add_node()  # c

        a = graph.get_node_by_id('a')
        b = graph.get_node_by_id('b')
        c = graph.get_node_by_id('c')

        graph.add_edge(a, b)
        graph.add_edge(c, b)

        a.data.add_distribution()
        a.data.get_distribution_by_id('0').parameters["loc"].change_current(-2.)
        a.data.get_distribution_by_id('1').parameters["loc"].change_current(2.)

        c.data.add_distribution()
        c.data.get_distribution_by_id('0').parameters["loc"].change_current(-4.)
        c.data.get_distribution_by_id('1').parameters["loc"].change_current(4.)

        formulas = ["sin(a) + cos(3.2+a)*c"]
        inputs = b.get_in_node_data()
        self.assertSetEqual(set(inputs.keys()), {"a", "c"})
        regression = RegressionMechanism(formulas, inputs)
        result = regression.transform(flatten=True)
        self.assertEqual(result.shape, (3000,))
        self.assertTrue(all(np.isfinite(result)))


class ClassficationMechanismTest(TestCase):
    def test_simple_classification_mechanism(self):
        formulas = ["a > 0.0"]
        inputs = [
            {
                "a": [-1., 2.],
            },
            {
                "a": [2., -1.],
            },
            {
                "a": [0., 0.],
            },
            {
                "a": [1.5, 2.2],
            }
        ]
        expecteds = [
            [[False, True], [True, False]],
            [[True, False], [False, True]],
            [[False, False], [True, True]],
            [[True, True], [False, False]]
        ]

        for input, expected in zip(inputs, expecteds):
            classification = ClassificationMechanism(formulas, input)
            result = classification.transform()
            self.assertListEqual(result.tolist(), expected)

    def test_complex_classification_mechanism(self):
        formulas = ["(a > 0.0) & ((abs(ceil(b)) < 1.0))"]
        inputs = [
            {
                "a": [-1., 2.],
                "b": [-0.8, -0.1]
            },
            {
                "a": [1., 2.],
                "b": [-0.8, -1.1]
            },
            {
                "a": [-1., 2.],
                "b": [-0.8, -1.1]
            },
            {
                "a": [1., 2.],
                "b": [-0.8, -0.9]
            },
        ]
        expecteds = [
            [[False, True], [True, False]],
            [[True, False], [False, True]],
            [[False, False], [True, True]],
            [[True, True], [False, False]]
        ]

        for input, expected in zip(inputs, expecteds):
            classification = ClassificationMechanism(formulas, input)
            result = classification.transform()
            self.assertListEqual(result.tolist(), expected)
