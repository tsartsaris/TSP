# -*- coding: utf-8 -*-
"""
Unit tests. Run them from the project folder with:

    python -m unittest discover tests

Each test checks one small piece against a known answer, so they double as
examples of how the modules are used.
"""

import os
import random
import tempfile
import unittest

from tsp_distance import euclidean_distance, geo_distance
from tsp_ga import (GeneticAlgorithm, _pmx_child, insertion_mutation, inversion_mutation,
                    one_point_crossover, pmx_crossover, repair, swap_mutation)
from tsp_ga_init_pop import create_initial_population, nearest_neighbour_tour
from tsp_parser import TSPFileError, TSPProblem, read_tour_file, read_tsp_file

PROBLEMS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TSP_Problems")


def load(name):
    return read_tsp_file(os.path.join(PROBLEMS, name + ".tsp"))


def is_valid_tour(tour, problem):
    """A valid tour visits every city exactly once."""
    return sorted(tour) == problem.cities


class DistanceTest(unittest.TestCase):

    def test_euclidean_distance_is_rounded(self):
        self.assertEqual(euclidean_distance((0, 0), (3, 4)), 5)
        self.assertEqual(euclidean_distance((0, 0), (1, 1)), 1)  # 1.414 rounds down
        self.assertEqual(euclidean_distance((0, 0), (1, 2)), 2)  # 2.236 rounds down
        self.assertEqual(euclidean_distance((0, 0), (2, 2)), 3)  # 2.828 rounds up

    def test_geo_distance_one_degree_along_equator(self):
        self.assertEqual(geo_distance((0.0, 0.0), (0.0, 1.0)), 112)

    def test_optimal_tours_have_the_published_length(self):
        # The lengths published by TSPLIB. Matching them proves that the distance
        # functions and the tour length follow the TSPLIB rules exactly.
        for name, optimal in [("berlin52", 7542), ("eil101", 629), ("a280", 2579), ("burma14", 3323)]:
            with self.subTest(problem=name):
                problem = load(name)
                tour = read_tour_file(os.path.join(PROBLEMS, name + ".opt.tour"))
                self.assertTrue(is_valid_tour(tour, problem))
                self.assertEqual(problem.tour_length(tour), optimal)

    def test_tour_length_includes_the_way_back(self):
        problem = TSPProblem("square", {1: (0, 0), 2: (0, 10), 3: (10, 10), 4: (10, 0)}, "EUC_2D")
        self.assertEqual(problem.tour_length([1, 2, 3, 4]), 40)


class ParserTest(unittest.TestCase):

    def write_file(self, text):
        handle, path = tempfile.mkstemp(suffix=".tsp")
        with os.fdopen(handle, "w") as tsp_file:
            tsp_file.write(text)
        self.addCleanup(os.remove, path)
        return path

    def test_reads_header_and_coordinates(self):
        problem = load("berlin52")
        self.assertEqual(problem.name, "berlin52")
        self.assertEqual(problem.edge_weight_type, "EUC_2D")
        self.assertEqual(len(problem.cities), 52)
        self.assertEqual(problem.coordinates[1], (565.0, 575.0))

    def test_rejects_unsupported_edge_weight_type(self):
        path = self.write_file("NAME: att3\nTYPE: TSP\nDIMENSION: 1\nEDGE_WEIGHT_TYPE: ATT\n"
                               "NODE_COORD_SECTION\n1 0 0\nEOF\n")
        with self.assertRaisesRegex(TSPFileError, "ATT is not supported"):
            read_tsp_file(path)

    def test_rejects_wrong_dimension(self):
        path = self.write_file("NAME: bad\nTYPE: TSP\nDIMENSION: 3\nEDGE_WEIGHT_TYPE: EUC_2D\n"
                               "NODE_COORD_SECTION\n1 0 0\n2 1 1\nEOF\n")
        with self.assertRaisesRegex(TSPFileError, "DIMENSION 3 but lists 2"):
            read_tsp_file(path)


class InitialPopulationTest(unittest.TestCase):

    def setUp(self):
        random.seed(1)
        self.problem = load("berlin52")

    def test_nearest_neighbour_always_takes_the_closest_city(self):
        tour = nearest_neighbour_tour(self.problem, 1)
        self.assertTrue(is_valid_tour(tour, self.problem))
        for i in range(len(tour) - 1):
            unvisited = tour[i + 1:]
            closest = min(self.problem.distance(tour[i], city) for city in unvisited)
            self.assertEqual(self.problem.distance(tour[i], tour[i + 1]), closest)

    def test_population_has_the_requested_size_and_valid_tours(self):
        for mode in ("shuffle", "elitism"):
            with self.subTest(mode=mode):
                tours = create_initial_population(self.problem, 60, mode)
                self.assertEqual(len(tours), 60)
                self.assertTrue(all(is_valid_tour(tour, self.problem) for tour in tours))

    def test_elitism_starts_from_better_tours_than_shuffle(self):
        best = {mode: min(map(self.problem.tour_length, create_initial_population(self.problem, 60, mode)))
                for mode in ("shuffle", "elitism")}
        self.assertLess(best["elitism"], best["shuffle"])


class OperatorTest(unittest.TestCase):

    def setUp(self):
        random.seed(2)
        self.problem = load("berlin52")

    def random_tour(self):
        return random.sample(self.problem.cities, len(self.problem.cities))

    def test_one_point_crossover_then_repair_gives_valid_tours(self):
        for _ in range(200):
            for child in one_point_crossover(self.random_tour(), self.random_tour()):
                self.assertTrue(is_valid_tour(repair(child, self.problem), self.problem))

    def test_pmx_example(self):
        # the example from the pmx_crossover docstring, segment = positions 2..4
        child = _pmx_child([1, 2, 3, 4, 5, 6, 7], [3, 7, 5, 1, 6, 4, 2], 2, 4)
        self.assertEqual(child, [6, 7, 3, 4, 5, 1, 2])

    def test_pmx_gives_valid_tours_without_repair(self):
        for _ in range(200):
            for child in pmx_crossover(self.random_tour(), self.random_tour()):
                self.assertTrue(is_valid_tour(child, self.problem))

    def test_mutations_give_valid_tours_and_leave_the_parent_alone(self):
        for mutation in (insertion_mutation, swap_mutation, inversion_mutation):
            with self.subTest(mutation=mutation.__name__):
                for _ in range(200):
                    parent = self.random_tour()
                    original = parent[:]
                    self.assertTrue(is_valid_tour(mutation(parent), self.problem))
                    self.assertEqual(parent, original)


class GeneticAlgorithmTest(unittest.TestCase):

    def test_best_tour_never_gets_worse_and_improves(self):
        random.seed(3)
        problem = load("berlin52")
        ga = GeneticAlgorithm(problem, create_initial_population(problem, 60, "shuffle"))
        start = ga.best_length
        previous = start
        for _ in range(300):
            ga.step()
            self.assertLessEqual(ga.best_length, previous)
            self.assertEqual(problem.tour_length(ga.best_tour), ga.best_length)
            previous = ga.best_length
        self.assertTrue(is_valid_tour(ga.best_tour, problem))
        self.assertLess(ga.best_length, start / 2)  # random tours are about 3x the optimum


if __name__ == "__main__":
    unittest.main()
