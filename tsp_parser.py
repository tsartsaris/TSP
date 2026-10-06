# -*- coding: utf-8 -*-
"""
Reading TSPLIB files.

A TSPLIB problem file (.tsp) is plain text: a header of "KEY : value" lines,
followed by a NODE_COORD_SECTION with one city per line and an EOF marker:

    NAME : berlin52
    TYPE : TSP
    DIMENSION : 52
    EDGE_WEIGHT_TYPE : EUC_2D
    NODE_COORD_SECTION
    1 565.0 575.0
    2 25.0 185.0
    ...
    EOF

A tour file (.opt.tour) lists the cities of a tour in visiting order after a
TOUR_SECTION line and ends the list with -1. The .opt.tour files in
TSP_Problems/ are the known optimal tours, handy for checking results.
"""

__author__ = "Tsartsaris Sotiris"
__copyright__ = "Copyright 2014, The TSP Project"
__license__ = "APACHE 2.0"

import os

from tsp_distance import DISTANCE_FUNCTIONS

# Above this many cities a full distance table would use too much memory,
# so distances are computed every time they are needed instead.
MAX_CITIES_FOR_DISTANCE_TABLE = 1000


class TSPFileError(Exception):
    """Raised when a file is not a TSPLIB problem this program can solve."""


class TSPProblem:
    """
        A loaded problem: the cities, their coordinates and the rule for
        measuring the distance between two of them.

        A *tour* is a list of city numbers in visiting order, e.g. [1, 5, 3, 2, 4].
        The salesman returns from the last city to the first, so that closing
        edge is always part of the tour length.
    """

    def __init__(self, name, coordinates, edge_weight_type):
        self.name = name
        self.coordinates = coordinates          # {city number: (x, y)}
        self.cities = sorted(coordinates)       # [1, 2, ..., n]
        self.edge_weight_type = edge_weight_type
        self._distance_function = DISTANCE_FUNCTIONS[edge_weight_type]

        # The genetic algorithm measures the same pairs of cities millions of
        # times, so for normal sized problems we compute every distance once,
        # up front, and afterwards just look it up: a classic speed for memory trade.
        self._table = None
        if len(self.cities) <= MAX_CITIES_FOR_DISTANCE_TABLE:
            size = max(self.cities) + 1
            self._table = [[0] * size for _ in range(size)]
            for a in self.cities:
                for b in self.cities:
                    self._table[a][b] = self._distance_function(coordinates[a], coordinates[b])

    def distance(self, city_a, city_b):
        """Distance between two cities, using the problem's EDGE_WEIGHT_TYPE."""
        if self._table is not None:
            return self._table[city_a][city_b]
        return self._distance_function(self.coordinates[city_a], self.coordinates[city_b])

    def tour_length(self, tour):
        """
            Total length of a closed tour. zip(tour, tour[1:] + tour[:1]) pairs every
            city with the next one and the last city with the first:
            [1, 2, 3] -> (1, 2), (2, 3), (3, 1)
        """
        return sum(self.distance(a, b) for a, b in zip(tour, tour[1:] + tour[:1]))

    def tour_coordinates(self, tour):
        """Coordinates of the cities of a tour, in visiting order (for plotting)."""
        return [self.coordinates[city] for city in tour]


def _read_lines(path):
    with open(path) as tsp_file:
        return [line.strip() for line in tsp_file]


def read_tsp_file(path):
    """
        Read a TSPLIB .tsp file and return a TSPProblem.
        Raises TSPFileError with a readable message if the file can't be used.
    """
    header = {}
    coordinates = {}
    in_coordinates = False

    for line in _read_lines(path):
        if not line:
            continue
        if line == "EOF":
            break
        if line == "NODE_COORD_SECTION":
            in_coordinates = True
        elif in_coordinates:
            # "1 565.0 575.0": the city number followed by its two coordinates
            parts = line.split()
            if len(parts) < 3:
                raise TSPFileError("Unexpected line in NODE_COORD_SECTION: %r" % line)
            coordinates[int(parts[0])] = (float(parts[1]), float(parts[2]))
        else:
            # "DIMENSION : 52" -> header["DIMENSION"] = "52"
            key, _, value = line.partition(":")
            header[key.strip()] = value.strip()

    name = header.get("NAME", os.path.splitext(os.path.basename(path))[0])
    problem_type = header.get("TYPE", "TSP")
    edge_weight_type = header.get("EDGE_WEIGHT_TYPE")

    if problem_type != "TSP":
        raise TSPFileError("%s is a %s problem, only symmetric TSP problems are supported" % (name, problem_type))
    if edge_weight_type not in DISTANCE_FUNCTIONS:
        raise TSPFileError("EDGE_WEIGHT_TYPE %s is not supported, only %s"
                           % (edge_weight_type, ", ".join(DISTANCE_FUNCTIONS)))
    if not coordinates:
        raise TSPFileError("%s has no NODE_COORD_SECTION with city coordinates" % name)
    if "DIMENSION" in header and int(header["DIMENSION"]) != len(coordinates):
        raise TSPFileError("%s declares DIMENSION %s but lists %d cities"
                           % (name, header["DIMENSION"], len(coordinates)))

    return TSPProblem(name, coordinates, edge_weight_type)


def read_tour_file(path):
    """Read a TSPLIB .tour file and return the tour as a list of city numbers."""
    tour = []
    in_tour = False
    for line in _read_lines(path):
        if line == "TOUR_SECTION":
            in_tour = True
        elif in_tour:
            for value in line.split():  # usually one city per line, but several are allowed
                if value == "-1":
                    return tour
                tour.append(int(value))
    return tour
