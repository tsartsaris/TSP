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
    to start from. Techniques to create are shuffle and elitism
    with NN (nearest neighbor) techniques
"""

import numpy as np
import random

from tsp_distance import euclidean_distance


class TSPInitialPopulation:
    def __init__(self, cities_dict, init_tour, pop_size, init_type="shuffle"):
        self.pop_group = []  # this is the entire population produced
        self.init_type = init_type  # this is the type of initialisation (shuffle or elitism)
        self.init_tour = init_tour  # the initial tour provided
        self.cities_dict = cities_dict  # the dictionary with city:coordinates
        self.pop_size = pop_size  # the initial amount of population that will be created
        self.random_remaining_cities = self.init_tour[:]
        self.random_cities = []
        if self.init_type == "shuffle":
            self.shuffle_list(self.init_tour, self.pop_size)
        elif self.init_type == "elitism":
            half = self.pop_size / 2
            self.shuffle_list(self.init_tour, half)
            for i in range(half):
                city = self.pick_random_city()
                self.create_nearest_tour(city)



    def shuffle_list(self, tour_list, pop_size):
        """
            We create a numpy array and we use permutation
            to create different arrays equal to the size of
            initial population
        """
        x = np.array(tour_list)
        while len(self.pop_group) < self.pop_size:
            y = np.random.permutation(x)
            if not any((y == x).all() for x in self.pop_group):
                self.pop_group.append(y.tolist())

    def find_nn(self, city, list):
        """
            Given a city we find the next nearest city
        """
        start_city = self.get_coordinates_from_city(city)
        return min((euclidean_distance(start_city, self.get_coordinates_from_city(rest)), rest) for rest in
                   list)


    def get_coordinates_from_city(self, city):
        """
            Given a city return the coordinates (x,y)
        """
        self.city_coords = self.cities_dict.get(city)
        return self.city_coords

    def pick_random_city(self):
        """
            Random pick of a city. Persist of uniqueness each time
            the city is added to the random city list and removed
            from remaining cities. Each time we pick a new one from
            the eliminated list of remaining cities
        """
        if self.random_remaining_cities:
            self.random_city = random.choice(self.random_remaining_cities)
            self.random_remaining_cities.remove(self.random_city)
            self.random_cities.append(self.random_city)
        return self.random_city

    def create_nearest_tour(self, city):
        prov_list = self.init_tour[:]
        nearest_tour = [city]
        if city in prov_list: prov_list.remove(city)
        while prov_list:
            current_city = nearest_tour[-1]
            next_city = self.find_nn(current_city, prov_list)
            nearest_tour.append(next_city[1])
            prov_list.remove(next_city[1])
        self.pop_group.append(nearest_tour)