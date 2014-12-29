# ! /usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Tsartsaris Sotiris"
__copyright__ = "Copyright 2014, The TSP Project"
__credits__ = ["Tsartsaris Sotiris"]
__license__ = "APACHE 2.0"
__version__ = "1.0.1"
__maintainer__ = "Tsartsaris Sotiris"
__email__ = "info@tsartsaris.gr"
__status__ = "Development"

"""
    Provided a dictionary with city coordinates and a list
    of the current tour it calculates the entire tour distance
"""

import math


class TSPDistance:
    def __init__(self, tourlist, citydict):
        self.cities_best = []
        self.tourlist = tourlist
        self.citydict = citydict
        for i in self.tourlist:
            self.cities_best.append(self.citydict.get(i))
        self.distance_cost = self.total_distance(self.cities_best)

    def distance(self, p0, p1):
        xdiff = float(p1[0]) - float(p0[0])
        ydiff = float(p1[1]) - float(p0[1])
        return int(math.sqrt((xdiff * xdiff + ydiff * ydiff) + 0.5))

    def total_distance(self, cities_best):
        cities_best = self.cities_best
        # print cities_tups
        return sum(self.distance(v, w) for v, w in zip(cities_best[:-1], cities_best[1:]))