# -*- coding: utf-8 -*-
import numpy as np
import unittest
from algorithms import weighted_distribution_calculator as wcalc


class TestWeightedDistribution(unittest.TestCase):
    def test1(self):
        weights_map = np.array([[1, 1, 1],
                                [1, 1, 1],
                                [2, 2, 2],
                                [2, 6, 2]])

        zone_map = np.array([[1, 1, 1],
                             [1, 1, 1],
                             [2, 2, 2],
                             [2, 2, 2]])

        zone_value = [0, 1, 2]

        result = wcalc.compute_weighted_distribution(np.NaN, weights_map, zone_map, zone_value)

        expect_result = np.array([[1 / 6, 1 / 6, 1 / 6],
                                  [1 / 6, 1 / 6, 1 / 6],
                                  [4 / 16, 4 / 16, 4 / 16],
                                  [4 / 16, 12 / 16, 4 / 16]])
        self.assertTrue(np.allclose(expect_result, result, equal_nan=True))

    def test2(self):
        weights_map = np.array([[1, 1, 1],
                                [1, 1, 1],
                                [2, 2, 2],
                                [2, 6, 2]])

        zone_map = np.array([[1, 1, 1],
                             [1, 1, 1],
                             [1, 1, 1],
                             [1, 1, 1]])

        zone_value = [0, 3]

        result = wcalc.compute_weighted_distribution(np.NaN, weights_map, zone_map, zone_value)

        expect_result = np.array([[3 / 22, 3 / 22, 3 / 22],
                                  [3 / 22, 3 / 22, 3 / 22],
                                  [6 / 22, 6 / 22, 6 / 22],
                                  [6 / 22, 18 / 22, 6 / 22]])
        self.assertTrue(np.allclose(expect_result, result, equal_nan=True))

    def test3(self):
        weights_map = np.array([[1, 1, 1],
                                [1, 1, 1],
                                [2, np.NaN, 2],
                                [2, 6, 2]])

        zone_map = np.array([[1, 1, 1],
                             [1, 1, 1],
                             [1, 1, 1],
                             [1, 1, 1]])

        zone_value = [0, 3]

        result = wcalc.compute_weighted_distribution(np.NaN, weights_map, zone_map, zone_value)

        expect_result = np.array([[3 / 20, 3 / 20, 3 / 20],
                                  [3 / 20, 3 / 20, 3 / 20],
                                  [6 / 20, np.NaN, 6 / 20],
                                  [6 / 20, 18 / 20, 6 / 20]])
        self.assertTrue(np.allclose(expect_result, result, equal_nan=True))


if __name__ == '__main__':
    unittest.main()
