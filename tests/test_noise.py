from models.noise import Data, Distribution
from unittest import TestCase
from unittest.mock import patch
import matplotlib.pyplot as plt


class DataTest(TestCase):
    def test_simple_distribution(self):
        data = Data.default_data('a')
        self.assertEqual(data.id, 'a')
        self.assertLessEqual(len(data.get_distributions()), 1)
        self.assertEqual(['0'], data.get_distribution_ids())

        distribution = data.distributions['0']
        assert distribution is not None, "invalid distribution"
        self.assertEqual(distribution.name, "normal")
        self.assertEqual(data.get_free_id(), '1')

        data.add_distribution()
        self.assertLessEqual(len(data.get_distributions()), 2)
        self.assertEqual(['0', '1'], data.get_distribution_ids())

        distribution = data.distributions['1']
        assert distribution is not None, "invalid distribution"
        self.assertEqual(distribution.name, "normal")
        self.assertEqual(data.get_free_id(), '2')

        to_remove = data.get_distribution_by_id('0')
        assert to_remove is not None, "invalid distribution"
        data.remove_distribution(to_remove)
        self.assertLessEqual(len(data.get_distributions()), 1)
        self.assertEqual(['1'], data.get_distribution_ids())

    @patch('models.noise.CONSTANTS.NR_DATA_POINTS', 120)
    def test_data_generation_simple(self):

        data = Data.default_data('a')
        data.get_distribution_by_id('0').change_distribution("lognorm")  # type: ignore
        data.get_distribution_by_id('0').get_parameter_by_name("loc").change_current(7)  # type: ignore
        data.get_distribution_by_id('0').get_parameter_by_name("scale").change_current(3)  # type: ignore

        values = data.generate_data()
        self.assertEqual(len(values), 1)
        self.assertEqual(len(values[0]), 120)
        # check graph in files
        plt.hist(values)
        plt.savefig("simple_distribution.png")
        plt.clf()

        data.add_distribution()
        data.get_distribution_by_id('0').change_distribution("normal")  # type: ignore
        data.get_distribution_by_id('0').get_parameter_by_name("loc").change_current(-3)  # type: ignore
        data.get_distribution_by_id('1').change_distribution("normal")  # type: ignore
        data.get_distribution_by_id('1').get_parameter_by_name("loc").change_current(3)  # type: ignore

        values = data.generate_data()
        self.assertEqual(len(values), 2)
        self.assertEqual(len(values[0]), 60)
        self.assertEqual(len(values[1]), 60)
        values = [v for vl in values for v in vl]
        # check graph in files
        plt.hist(values)
        plt.savefig("double_distribution.png")
        plt.clf()

        data.add_distribution()
        data.get_distribution_by_id('0').change_distribution("normal")  # type: ignore
        data.get_distribution_by_id('0').get_parameter_by_name("loc").change_current(-4)  # type: ignore
        data.get_distribution_by_id('1').change_distribution("normal")  # type: ignore
        data.get_distribution_by_id('1').get_parameter_by_name("loc").change_current(0)  # type: ignore
        data.get_distribution_by_id('2').change_distribution("normal")  # type: ignore
        data.get_distribution_by_id('2').get_parameter_by_name("loc").change_current(4)  # type: ignore

        values = data.generate_data()
        self.assertEqual(len(values), 3)
        self.assertEqual(len(values[0]), 40)
        self.assertEqual(len(values[1]), 40)
        self.assertEqual(len(values[2]), 40)
        values = [v for vl in values for v in vl]
        # check graph in files
        plt.hist(values)
        plt.savefig("triple_distribution.png")


class DistributionTest(TestCase):
    def test_simple_distribution(self):
        distribution = Distribution.get_distribution('0', "lognorm")
        self.assertEqual(distribution.id, '0')
        self.assertEqual(distribution.name, "lognorm")
        self.assertListEqual(["loc", "scale", "s"], distribution.get_parameter_names())
        self.assertEqual(distribution.get_parameter_by_name("loc").current, 0.)
        # valid changes
        distribution.get_parameter_by_name("loc").change_current(7)
        self.assertEqual(distribution.get_parameter_by_name("loc").current, 7.)
        distribution.get_parameter_by_name("scale").change_current(3)
        self.assertEqual(distribution.get_parameter_by_name("scale").current, 3.)
        distribution.get_parameter_by_name("s").change_current(2)
        self.assertEqual(distribution.get_parameter_by_name("s").current, 2)
        # invalid changes
        distribution.get_parameter_by_name("loc").change_current(100)
        self.assertEqual(distribution.get_parameter_by_name("loc").current, 10.)
        distribution.get_parameter_by_name("loc").change_current(-100)
        self.assertEqual(distribution.get_parameter_by_name("loc").current, -10.)
        distribution.get_parameter_by_name("scale").change_current(100)
        self.assertEqual(distribution.get_parameter_by_name("scale").current, 5.)
        distribution.get_parameter_by_name("scale").change_current(-100)
        self.assertEqual(distribution.get_parameter_by_name("scale").current, 0.)
        distribution.get_parameter_by_name("s").change_current(100)
        self.assertEqual(distribution.get_parameter_by_name("s").current, 5.)
        distribution.get_parameter_by_name("s").change_current(-100)
        self.assertEqual(distribution.get_parameter_by_name("s").current, 0.)

        # change distribution -> init values
        distribution.change_distribution("binom")
        self.assertEqual(distribution.name, "binom")
        self.assertListEqual(["n", "p"], distribution.get_parameter_names())
        self.assertEqual(distribution.get_parameter_by_name("n").current, 1)
        self.assertEqual(distribution.get_parameter_by_name("p").current, 0.5)

