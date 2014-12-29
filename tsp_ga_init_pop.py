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
    Provided a list representing a tour we create here
    the initial population for the Genetic Algorithm
    to start from. Techniques to create are shuffle...
"""

import numpy as np


class TSPInitialPopulation:
    def __init__(self, tour_list, pop_size, init_type="shuffle"):
        self.pop_group = []
        self.init_type = init_type
        self.tour_list = tour_list
        self.pop_size = pop_size
        if self.init_type == "shuffle":
            self.shuffle_list(self.tour_list, self.pop_size)
            print self.pop_group
            print len(self.pop_group)

    def shuffle_list(self, tour_list, pop_size):
        """
            We create a numpy array and we use permutation
            to create different arrays equal to the size of
            initial population
        """
        x = np.array(tour_list)
        for i in range(pop_size):
            y = np.random.permutation(x)
            if not any((y == x).all() for x in self.pop_group):
                self.pop_group.append(y)