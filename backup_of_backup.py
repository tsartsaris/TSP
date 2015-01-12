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
    Provided with the initial population first we apply a fitness function
    which will be the division of the tour distance divided by the best distance
    we have after each iteration. Then we apply a roulette-wheel selection on the population
    to get from the accumulated fitness of each tour a random pick
"""

from operator import itemgetter
import random


class TSPGeneticAlgo:
    def __init__(self, initial_population, city_tour_init, total_best):
        self.groups_of_two = []
        self.all_fitness = []
        self.initial_population = initial_population
        self.tour_init = city_tour_init
        self.total_best = total_best[0]
        self.calculate_fitness(self.initial_population)
        self.random_pick_doubles(self.all_fitness)
        print self.groups_of_two

    def fitness_function(self, city_cost):
        """
            We apply the fitness function to each distance by
            dividing the lowest with each one of them
        """
        return round(float(float(self.total_best) / float(city_cost)), 3)

    def calculate_fitness(self, in_list):
        """
            Given a list of distances we apply the fitness function to each
            one of them
        """
        for city_distance in in_list:
            self.all_fitness.append([self.fitness_function(city_distance[0]), city_distance[1]])

    def sorted_all_fintess(self):
        self.sorted_fitness = sorted(self.all_fitness, key=itemgetter(0))

    def random_pick_doubles(self, in_list):
        """
            We iterate the selected population and we create groups of 2
            to make the breeding in the next step.
        """
        while in_list:
            local = random.sample(in_list, 2)
            for i in local:
                in_list.remove(i)
            self.groups_of_two.append(local)