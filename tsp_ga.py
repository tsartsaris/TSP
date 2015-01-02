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
import numpy as np
import random
import collections


class TSPGeneticAlgo:
    def __init__(self, initial_population, city_tour_init):
        self.city_tour_init = city_tour_init  # pass the initial tour here for differences between children after crossover duplicates
        print self.city_tour_init
        self.children_dirty = []
        self.all_fitness = []
        self.groups_of_two = []
        self.total_best = 10000000000000000000000000000000000
        self.initial_population = initial_population
        self.current_best = self.current_best_score(self.initial_population)
        self.selected_population = []
        if self.current_best < self.total_best:
            self.total_best = self.current_best
        self.calculate_fitness(self.initial_population)
        self.accumulated_list = self.accumulate_fitness()
        self.roulette_wheel_selection(self.accumulated_list)
        for i in range(50):
            self.selected_population.append(self.roulette_wheel_selection(self.accumulated_list))
        self.random_pick_doubles(self.selected_population)
        self.children_dirty = self.crossover_genetic_operator(self.groups_of_two)
        self.remove_duplicate_cities(self.children_dirty)

    def fitness_function(self, city_cost):
        """
            We apply the fitness function to each distance by
            dividing the lowest with each one of them
        """
        return float(float(self.total_best) / float(city_cost))

    @staticmethod
    def current_best_score(array):
        """
            This is the lowest distance form the population
            we will use it in the fitness function
        """
        return min(i[0] for i in array)

    def calculate_fitness(self, in_list):
        """
            Given a list of distances we apply the fitness function to each
            one of them
        """
        for city_distance in in_list:
            self.all_fitness.append([self.fitness_function(city_distance[0]), city_distance[1]])

    def accumulate_fitness(self):
        """
            Given a list of fitness values, we sort them from lower to higher
            and the we accumulate those values. Last element should have a fitness of 1
        """
        sum1 = sum(pair[0] for pair in self.all_fitness)
        for value in self.all_fitness:
            value[0] = value[0] / sum1
        sorted_fit = sorted(self.all_fitness, key=itemgetter(0))
        unzipped_list = zip(*sorted_fit)
        accumulated_list = np.cumsum(unzipped_list[0])
        accumulated_fitness = zip(accumulated_list, unzipped_list[1])
        return accumulated_fitness

    @staticmethod
    def roulette_wheel_selection(accumulated_list):
        """
            iterating a range we get each time a random number from 0 to 1
            theν we iterate the sorted list of accumulated fitness values and we get
             the first higher from that number removing it from the list
        """
        random_number = random.random()
        for element in accumulated_list:
            if element[0] > random_number:
                accumulated_list.remove(element)
                return element

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

    def crossover_genetic_operator(self, in_list):
        local_doubles = []
        local_children = []
        for double in in_list:
            if double[0][1][0]:
                local_doubles.append(double[0][1][0])
            if double[1][1][0]:
                local_doubles.append(double[1][1][0])
        local_doubles = map(None, *[iter(local_doubles)] * 2)
        for pair in local_doubles:
            ind1 = pair[0]
            ind2 = pair[1]
            size = min(len(ind1), len(ind2))
            cxpoint = random.randint(1, size - 1)
            ind1[cxpoint:], ind2[cxpoint:] = ind2[cxpoint:], ind1[cxpoint:]
            local_children.append(ind1)
            local_children.append(ind2)
        return local_children

    def remove_duplicate_cities(self, in_list):
        for dirty in in_list:
            differs = [x for x in self.city_tour_init if x not in dirty]
            print differs
            uniq = [x for x, y in collections.Counter(dirty).items() if y > 1]
            print uniq
            for unique in uniq:
                print dirty.index(unique)