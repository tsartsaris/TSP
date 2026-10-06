# -*- coding: utf-8 -*-
"""
The initial population: the first generation of tours the genetic algorithm
starts from.

Two ways of creating it are offered:

    shuffle   every tour is a random ordering of the cities. Random tours are
              very long, but they are diverse: they give the algorithm lots of
              different material to combine.

    elitism   half of the population are nearest neighbour tours (see below),
              the other half are random. The algorithm starts from much better
              tours, at the price of less diversity.

Nearest neighbour is the simplest *greedy* heuristic for the TSP: start
somewhere and always travel to the closest city you haven't visited yet. It is
fast and usually lands within about 25% of the optimal length, but it never
looks ahead, so it typically ends with a few very long edges back across the map.
"""

__author__ = "Tsartsaris Sotiris"
__copyright__ = "Copyright 2014, The TSP Project"
__license__ = "APACHE 2.0"

import math
import random

INIT_SHUFFLE = "shuffle"
INIT_ELITISM = "elitism"
INIT_MODES = (INIT_SHUFFLE, INIT_ELITISM)


def nearest_neighbour_tour(problem, start_city, cities=None):
    """
        Greedy tour: begin at start_city and repeatedly move to the nearest
        city not yet visited, until every city is in the tour.

        cities limits the tour to a subset of the problem's cities (the start
        city included); the genetic algorithm uses this to repair children.
    """
    unvisited = set(problem.cities if cities is None else cities)
    unvisited.discard(start_city)
    tour = [start_city]
    while unvisited:
        current = tour[-1]
        # min() with a key returns the city whose distance from current is smallest
        nearest = min(unvisited, key=lambda city: problem.distance(current, city))
        tour.append(nearest)
        unvisited.remove(nearest)
    return tour


def random_tours(cities, count):
    """
        count different random orderings of the cities. A set of tuples
        remembers the tours already made, so no tour appears twice.
    """
    # there are only n! orderings, so a tiny problem can't fill a big population
    count = min(count, math.factorial(len(cities)))
    seen = set()
    tours = []
    while len(tours) < count:
        tour = random.sample(cities, len(cities))  # a shuffled copy
        if tuple(tour) not in seen:
            seen.add(tuple(tour))
            tours.append(tour)
    return tours


def create_initial_population(problem, size, mode=INIT_SHUFFLE):
    """
        Return a list of size tours for the first generation, created
        with mode "shuffle" or "elitism" (see the module docstring).
    """
    if mode == INIT_SHUFFLE:
        return random_tours(problem.cities, size)
    if mode == INIT_ELITISM:
        # one greedy tour per start city; a problem has only as many start cities as cities
        greedy_count = min(size // 2, len(problem.cities))
        start_cities = random.sample(problem.cities, greedy_count)
        greedy = [nearest_neighbour_tour(problem, city) for city in start_cities]
        return greedy + random_tours(problem.cities, size - greedy_count)
    raise ValueError("Unknown initial population mode %r, use one of %s" % (mode, INIT_MODES))
