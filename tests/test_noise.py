from unittest import TestCase
from unittest.mock import patch

import matplotlib.pyplot as plt

from models.noise import Distribution, Noise


class DataTest(TestCase):
    def test_simple_distribution(self):
        noise = Noise.default_noise("a")
        self.assertEqual(noise.id_, "a")
        self.assertLessEqual(len(noise.get_distributions()), 1)
        self.assertEqual(["0"], noise.get_distribution_ids())

        distribution = noise.sub_distributions["0"]
        assert distribution is not None, "invalid distribution"
        self.assertEqual(distribution.name, "normal")
        self.assertEqual(noise.get_free_id(), "1")

        noise.add_distribution()
        self.assertLessEqual(len(noise.get_distributions()), 2)
        self.assertEqual(["0", "1"], noise.get_distribution_ids())

        distribution = noise.sub_distributions["1"]
        assert distribution is not None, "invalid distribution"
        self.assertEqual(distribution.name, "normal")
        self.assertEqual(noise.get_free_id(), "2")

        to_remove = noise.get_distribution_by_id("0")
        assert to_remove is not None, "invalid distribution"
        noise.remove_distribution(to_remove)
        self.assertLessEqual(len(noise.get_distributions()), 1)
        self.assertEqual(["1"], noise.get_distribution_ids())

    @patch("models.noise.CONSTANTS.NR_DATA_POINTS", 120)
    def test_data_generation_simple(self):

        noise = Noise.default_noise("a")
        distr_0 = noise.get_distribution_by_id("0")
        assert distr_0 is not None
        distr_0.change_distribution("lognorm")
        param_loc = distr_0.get_parameter_by_name("loc")
        assert param_loc is not None
        param_loc.change_current(7.0)
        param_scale = distr_0.get_parameter_by_name("loc")
        assert param_scale is not None
        param_scale.change_current(3.0)

        values = noise.generate_data()
        self.assertEqual(len(values), 120)

        # check graph in files
        plt.hist(values)
        plt.savefig("simple_distribution.png")
        plt.clf()

        distr_0.change_distribution("normal")
        param_loc = distr_0.get_parameter_by_name("loc")
        assert param_loc is not None
        param_loc.change_current(-3)

        noise.add_distribution()
        distr_1 = noise.get_distribution_by_id("1")
        assert distr_1 is not None

        distr_1.change_distribution("normal")
        param_loc = distr_1.get_parameter_by_name("loc")
        assert param_loc is not None
        param_loc.change_current(3)

        values = noise.generate_data()
        self.assertEqual(len(values), 120)
        # check graph in files
        plt.hist(values)
        plt.savefig("double_distribution.png")
        plt.clf()

        distr_0.change_distribution("normal")
        param_loc = distr_0.get_parameter_by_name("loc")
        assert param_loc is not None
        param_loc.change_current(-4)

        distr_1.change_distribution("normal")
        param_loc = distr_1.get_parameter_by_name("loc")
        assert param_loc is not None
        param_loc.change_current(0)

        noise.add_distribution()
        distr_2 = noise.get_distribution_by_id("2")
        assert distr_2 is not None
        distr_2.change_distribution("normal")
        param_loc = distr_2.get_parameter_by_name("loc")
        assert param_loc is not None
        param_loc.change_current(4)

        values = noise.generate_data()
        self.assertEqual(len(values), 120)
        # check graph in files
        plt.hist(values)
        plt.savefig("triple_distribution.png")


class DistributionTest(TestCase):
    def test_simple_distribution(self):
        distribution = Distribution.get_distribution("0", "lognorm")
        assert distribution is not None
        self.assertEqual(distribution.id_, "0")
        self.assertEqual(distribution.name, "lognorm")
        self.assertListEqual(["loc", "scale", "s"], distribution.get_parameter_names())
        param_loc = distribution.get_parameter_by_name("loc")
        assert param_loc is not None
        self.assertEqual(param_loc.current, 0.0)

        # valid changes
        param_loc.change_current(7)
        self.assertEqual(param_loc.current, 7.0)
        param_scale = distribution.get_parameter_by_name("scale")
        assert param_scale is not None
        param_scale.change_current(3)
        self.assertEqual(param_scale.current, 3.0)
        param_s = distribution.get_parameter_by_name("s")
        assert param_s is not None
        param_s.change_current(0.8)
        self.assertEqual(param_s.current, 0.8)

        # invalid changes
        param_loc.change_current(100)
        self.assertEqual(param_loc.current, 10.0)
        param_loc.change_current(-100)
        self.assertEqual(param_loc.current, -10.0)
        param_scale.change_current(100)
        self.assertEqual(param_scale.current, 5.0)
        param_scale.change_current(-100)
        self.assertEqual(param_scale.current, 0.0)
        param_s = distribution.get_parameter_by_name("s")
        assert param_s is not None
        param_s.change_current(100)
        self.assertEqual(param_s.current, 1.0)
        param_s.change_current(-100)
        self.assertEqual(param_s.current, 0.1)

        # change distribution -> init values
        distribution.change_distribution("binom")
        self.assertEqual(distribution.name, "binom")
        self.assertListEqual(["n", "p"], distribution.get_parameter_names())
        param_n = distribution.get_parameter_by_name("n")
        assert param_n is not None
        param_p = distribution.get_parameter_by_name("p")
        assert param_p is not None
        self.assertEqual(param_n.current, 1)
        self.assertEqual(param_p.current, 0.5)
