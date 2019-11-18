import PLANHEAT.algorithms.dasymap_calculator as dasymap
import unittest
import numpy as np


class TestDasymap(unittest.TestCase):
    def test_dasymap1(self):
        cols = 3
        rows = 4
        cat_map = np.array([[1, 1, 1],
                            [2, 1, 1],
                            [2, 2, 1],
                            [2, 2, 2]])

        zone_map = np.array([[1, 2, 3],
                             [1, 2, 3],
                             [1, 2, 3],
                             [1, 2, 3]])

        weights = np.array([0, 1, 2])
        demands = np.array([0, 300, 300, 300])

        result = dasymap.calculate(np.NaN, cat_map, weights, zone_map, demands)

        expected = np.array([[300 * 1.0 / 7.0, 300 * 1.0 / 6.0, 300 * 1.0 / 5.0],
                             [300 * 2.0 / 7.0, 300 * 1.0 / 6.0, 300 * 1.0 / 5.0],
                             [300 * 2.0 / 7.0, 300 * 2.0 / 6.0, 300 * 1.0 / 5.0],
                             [300 * 2.0 / 7.0, 300 * 2.0 / 6.0, 300 * 2.0 / 5.0]])
        print(result)
        self.assertTrue(np.allclose(expected, result, equal_nan=True))

    def test_dasymap2(self):
        cols = 3
        rows = 4

        cat_map = np.array([[2, 1, 1],
                            [2, 2, 1],
                            [2, 2, 2],
                            [2, 2, 2]])

        zone_map = np.array([[1, 2, 3],
                             [1, 2, 3],
                             [1, 2, 3],
                             [1, 2, 3]])

        weights = np.array([0, 1, 2])
        demands = np.array([0, 300, 300, 300])

        result = dasymap.calculate( np.NaN, cat_map, weights, zone_map, demands)

        expected = np.array([[75, 100, 90],
                             [75, 66.6666, 90],
                             [75, 66.6666, 60],
                             [75, 66.6666, 60]])

        self.assertTrue(np.allclose(expected, result, equal_nan=True))

    def test_dasymap3(self):
        cols = 3
        rows = 4

        cat_map = np.array([[2, 1, 1],
                            [2, 2, 1],
                            [2, 2, 2],
                            [2, 2, 2]])

        zone_map = np.array([[1, 2, 3],
                             [1, 2, 3],
                             [1, 2, 3],
                             [1, 2, 3]])

        weights = np.array([0, 1, 3])
        demands = np.array([0, 300, 300, 300])

        result = dasymap.calculate( np.NaN, cat_map, weights, zone_map, demands)

        expected = np.array([[75, 75, 75],
                             [75, 75, 75],
                             [75, 75, 75],
                             [75, 75, 75]])

        self.assertTrue(np.allclose(expected, result, equal_nan=True))

    def test_dasymap4(self):
        cols = 3
        rows = 4

        cat_map = np.array([[1, 0, 1],
                            [2, 0, 1],
                            [2, 0, 1],
                            [2, 0, 2]])

        zone_map = np.array([[1, 2, 3],
                             [1, 2, 3],
                             [1, 2, 3],
                             [1, 2, 3]])

        weights = np.array([0, 1, 2])
        demands = np.array([0, 300, 300, 300])

        result = dasymap.calculate(np.NaN, cat_map, weights, zone_map, demands)

        expected = np.array([[300 * 1.0 / 7.0, 75, 300 * 1.0 / 5.0],
                             [300 * 2.0 / 7.0, 75, 300 * 1.0 / 5.0],
                             [300 * 2.0 / 7.0, 75, 300 * 1.0 / 5.0],
                             [300 * 2.0 / 7.0, 75, 300 * 2.0 / 5.0]])

        self.assertTrue(np.allclose(expected, result, equal_nan=True))

    def test_dasymap5(self):
        cols = 3
        rows = 4

        cat_map = np.array([[1, 1, 1],
                            [2, 1, 1],
                            [2, 2, 1],
                            [2, 2, 2]])

        zone_map = np.array([[1, 0, 3],
                             [1, 0, 3],
                             [1, 0, 3],
                             [1, 0, 3]])

        weights = np.array([0, 1, 2])
        demands = np.array([6, 300, 300, 300])

        result = dasymap.calculate( np.NaN, cat_map, weights, zone_map, demands)

        expected = np.array([[300 * 1.0 / 7.0, 1, 300 * 1.0 / 5.0],
                             [300 * 2.0 / 7.0, 1, 300 * 1.0 / 5.0],
                             [300 * 2.0 / 7.0, 2, 300 * 1.0 / 5.0],
                             [300 * 2.0 / 7.0, 2, 300 * 2.0 / 5.0]])

        self.assertTrue(np.allclose(expected, result, equal_nan=True))

    def test_dasymap6(self):
        cols = 3
        rows = 4

        cat_map = np.array([[0, 0, 0],
                            [0, 0, 0],
                            [0, 0, 0],
                            [0, 0, 0]])

        zone_map = np.array([[0, 0, 0],
                             [0, 0, 0],
                             [0, 0, 0],
                             [0, 0, 0]])

        weights = np.array([0, 1, 2])
        demands = np.array([0, 300, 300, 300])

        result = dasymap.calculate(np.NaN, cat_map, weights, zone_map, demands)

        expected = np.array([[0, 0, 0],
                             [0, 0, 0],
                             [0, 0, 0],
                             [0, 0, 0]])

        self.assertTrue(np.allclose(expected, result, equal_nan=True))

    def test_dasymap7a(self):
        cols = 3
        rows = 4

        cat_map = np.array([[1, 0, 0],
                            [2, 1, 0],
                            [2, 2, 1],
                            [2, 2, 2]])

        zone_map = np.array([[0, 0, 0],
                             [0, 0, 0],
                             [0, 0, 0],
                             [0, 0, 0]])

        weights = np.array([0.33333, 0, 0.66666])
        demands = np.array([9])

        result = dasymap.calculate( np.NaN, cat_map, weights, zone_map, demands)

        expected = np.array([[0, 1, 1],
                             [1, 0, 1],
                             [1, 1, 0],
                             [1, 1, 1]])

        self.assertTrue(np.allclose(expected, result, equal_nan=True))

    def test_dasymap7b(self):
        cols = 3
        rows = 4

        cat_map = np.array([[1, 0, 0],
                            [2, 1, 0],
                            [2, 2, 1],
                            [2, 2, 2]])

        zone_map = np.array([[0, 0, 0],
                             [0, 0, 0],
                             [0, 0, 0],
                             [0, 0, 0]])

        weights = np.array([1, 0, 2, 3])
        demands = np.array([9, 300, 300, 300])

        result = dasymap.calculate( np.NaN, cat_map, weights, zone_map, demands)
        expected = np.array([[0, 1, 1],
                             [1, 0, 1],
                             [1, 1, 0],
                             [1, 1, 1]])

        self.assertTrue(np.allclose(expected, result, equal_nan=True))

    def test_dasymap8(self):
        cols = 3
        rows = 4

        cat_map = np.array([[1, 1, 1],
                            [1, 2, 1],
                            [1, 2, 1],
                            [1, 1, 1]])

        zone_map = np.array([[1, 1, 1],
                             [1, 1, 1],
                             [1, 1, 1],
                             [1, 1, 1]])

        weights = np.array([0, 0.1, 0.9])
        demands = np.array([0, 100])

        result = dasymap.calculate( np.NaN, cat_map, weights, zone_map, demands)
        expected = np.array([[1, 1, 1],
                             [1, 45, 1],
                             [1, 45, 1],
                             [1, 1, 1]])

        self.assertTrue(np.allclose(expected, result, equal_nan=True))

    def test_dasymap9(self):
        cols = 3
        rows = 4

        cat_map = np.array([[1, 1, 1],
                            [1, 2, 1],
                            [1, 1, 1],
                            [1, 1, 0]])

        zone_map = np.array([[1, 1, 1],
                             [1, 1, 1],
                             [1, 1, 1],
                             [1, 1, 1]])

        weights = np.array([0, 0.1, 0.9])
        demands = np.array([0, 100])

        result = dasymap.calculate(np.NaN, cat_map, weights, zone_map, demands)
        expected = np.array([[1, 1, 1],
                             [1, 90, 1],
                             [1, 1, 1],
                             [1, 1, 0]])

        self.assertTrue(np.allclose(expected, result, equal_nan=True))

    def test_dasymap10a(self):
        cols = 3
        rows = 4

        cat_map = np.array([[1, 1, 1],
                            [2, 2, 2],
                            [2, 2, 2],
                            [1, 1, 1]])

        zone_map = np.array([[1, 2, 3],
                             [1, 2, 3],
                             [1, 2, 3],
                             [1, 2, 3]])

        weights = np.array([0, 0.1, 0.9])
        demands = np.array([0, 100, 100, 100])

        result = dasymap.calculate(np.NaN, cat_map, weights, zone_map, demands)
        expected = np.array([[5, 5, 5],
                             [45, 45, 45],
                             [45, 45, 45],
                             [5, 5, 5]])

        self.assertTrue(np.allclose(expected, result, equal_nan=True))

    def test_dasymap10b(self):
        cols = 3
        rows = 4

        cat_map = np.array([[1, 1, 1],
                            [2, 2, 2],
                            [1, 1, 1],
                            [1, 1, 1]])

        zone_map = np.array([[1, 2, 3],
                             [1, 2, 3],
                             [1, 2, 3],
                             [1, 2, 3]])

        weights = np.array([0, 0.1, 0.9])
        demands = np.array([0, 100, 100, 100])

        result = dasymap.calculate( np.NaN, cat_map, weights, zone_map, demands)
        expected = np.array([[10 / 3.0, 10 / 3.0, 10 / 3.0],
                             [90, 90, 90],
                             [10 / 3.0, 10 / 3.0, 10 / 3.0],
                             [10 / 3.0, 10 / 3.0, 10 / 3.0]])

        self.assertTrue(np.allclose(expected, result, equal_nan=True))

    def test_dasymap10c(self):
        cols = 3
        rows = 4

        cat_map = np.array([[1, 1, 1],
                            [2, 2, 2],
                            [2, 2, 2],
                            [2, 2, 2]])

        zone_map = np.array([[1, 2, 3],
                             [1, 2, 3],
                             [1, 2, 3],
                             [1, 2, 3]])

        weights = np.array([0, 0.1, 0.9])
        demands = np.array([0, 100, 100, 100])

        result = dasymap.calculate( np.NaN, cat_map, weights, zone_map, demands)
        expected = np.array([[10, 10, 10],
                             [30, 30, 30],
                             [30, 30, 30],
                             [30, 30, 30]])

        self.assertTrue(np.allclose(expected, result, equal_nan=True))

    def test_dasymap11(self):
        cols = 3
        rows = 5

        cat_map = np.array([[float('nan'), 0, 1],
                            [float('nan'), 1, 0],
                            [2, 2, 1],
                            [0, 2, 2],
                            [float('nan'), 0, 2]], dtype='f')

        zone_map = np.array([[0, 0, 0],
                             [1, 2, 3],
                             [1, 2, 3],
                             [1, 2, 3],
                             [float('nan'), float('nan'), float('nan')]], dtype='f')

        expect_result = np.array([[0, 0, 0],
                                  [0, 8.47458, 0],
                                  [100, 45.7627, 15.625],
                                  [0, 45.7627, 84.375],
                                  [float('nan'), float('nan'), float('nan')]], dtype='f')

        weights = np.array([0.0, 0.1, 0.9])
        demands = np.array([0.0, 100.0, 100.0, 100.0])

        result = dasymap.calculate( np.NaN, cat_map, weights, zone_map, demands)
        self.assertTrue(np.allclose(expect_result, result, equal_nan=True))


if __name__ == '__main__':
    unittest.main()
