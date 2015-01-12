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
        self.elitism_population_for_mutation = []
        self.elitism_population_to_keep = []
        self.elitism_group = []  # this is to store NN tours before mutation
        self.elitism_population = 0
        self.shuffle_population = 0
        self.pop_group = []  # this is the entire population produced
        self.init_type = init_type  # this is the type of initialisation (shuffle or elitism)
        self.init_tour = init_tour  # the initial tour provided
        self.cities_dict = cities_dict  # the dictionary with city:coordinates
        self.pop_size = pop_size  # the initial amount of population that will be created
        self.random_remaining_cities = self.init_tour[:]
        self.random_cities = []
        self.create_the_initial_population()


    def create_the_initial_population(self):
        if self.init_type == "shuffle":
            self.shuffle_population = self.pop_size
            self.shuffle_list(self.init_tour, self.shuffle_population)
        elif self.init_type == "elitism":
            self.population_analysis()
            self.shuffle_list(self.init_tour, self.shuffle_population)
            for i in range(self.elitism_population):
                city = self.pick_random_city()
                self.create_nearest_tour(city)
            self.mutate_elitism()


    def shuffle_list(self, tour_list, pop_size):
        """
            We create a numpy array and we use permutation
            to create different arrays equal to the size of
            initial population
        """
        x = np.array(tour_list)
        while len(self.pop_group) < self.shuffle_population:
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
        return self.cities_dict.get(city)


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
        self.elitism_group.append(nearest_tour)

    def population_analysis(self):
        tour_population = len(self.init_tour)
        if tour_population < self.pop_size / 2:
            self.elitism_population = tour_population
            self.shuffle_population = self.pop_size - self.elitism_population
        else:
            self.elitism_population = self.pop_size / 2
            self.shuffle_population = self.pop_size / 2

    def mutate_elitism(self):
        for tour in self.elitism_group:
	        self.pop_group.append(tour)
	        # if random.getrandbits(1) == 1:
	        # self.elitism_population_for_mutation.append(tour)
	        #     else:
	        #         self.pop_group.append(tour)
	        #
	        # for elit_tour in self.elitism_population_for_mutation:
	        #     coin = random.randint(1, 3)
	        #     if coin == 1:
	        #         mutated = self.inversion_mutation(elit_tour)
	        #         self.pop_group.append(mutated)
	        #     elif coin == 2:
	        #         mutated = self.reciprocal_exchange_mutation(elit_tour)
	        #         self.pop_group.append(mutated)
	        #     else:
	        #         mutated = self.insertion_mutation(elit_tour)
	        #         self.pop_group.append(mutated)

    @staticmethod
    def insertion_mutation(in_list):
        tour_range = len(in_list)
        randomip = random.randint(0, tour_range)
        city_to_insert = in_list.pop()
        in_list.insert(randomip, city_to_insert)
        return in_list

    @staticmethod
    def reciprocal_exchange_mutation(in_list):
        a = random.randint(0, len(in_list) - 1)
        b = random.randint(0, len(in_list) - 1)
        in_list[b], in_list[a] = in_list[a], in_list[b]
        return in_list

    @staticmethod
    def inversion_mutation(in_list):
        a = random.randint(0, len(in_list) - 1)
        b = random.randint(0, len(in_list) - 1)
        if a < b:
            a = a
            b = b
        elif a > b:
            a = b
            b = a
        else:
            pass
        first, second, third = in_list[:a], in_list[a:b], in_list[b:]
        in_list = first + second[::-1] + third
        return in_list
