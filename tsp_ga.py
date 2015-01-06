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
import collections

from tsp_distance import *


class TSPGeneticAlgo:
    def __init__(self, initial_population, city_tour_init, city_coords, total_best):
        self.city_coords = city_coords
        self.children_dirty = []
        self.groups_of_two = []
        self.selected_for_breeding = []  # here we store the population selected from the tournament selection
        self.population_for_crossover = []  # based on the probability of crossover a equal random sample appended
        self.population_for_mutation = []  # the remainders from the above go here for mutation operation
        self.all_fitness = []
        self.offsprings = []  # this is where we are going to store all offsprings for later breeding
        self.initial_population = initial_population
        self.tour_init = city_tour_init
        self.total_best = total_best[0]
        self.calculate_fitness(self.initial_population)
        self.tournament_selection(self.all_fitness)
        self.divide_breeding_mut_cross(self.selected_for_breeding,
                                       0.8)  # produces population for crossover and mutation
        self.children_dirty = self.one_point_crossover(self.population_for_crossover)
        self.remove_duplicate_cities(self.children_dirty)

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

    def tournament_selection(self, in_list):
        """
            We iterate the selected population and we create groups of 2
            to make the breeding in the next step.
        """
        while in_list:
            local = random.sample(in_list, 2)
            for i in local:
                in_list.remove(i)
            best = max(i[0] for i in local)
            for dub in local:
                if dub[0] == best:
                    self.selected_for_breeding.append(dub)

    def random_pick_doubles(self, in_list):
        """
            We iterate the selected population and we create groups of 2
            to make the breeding in the next step.
        """
        if (len(in_list) % 2) != 0:
            in_list.pop()
        while in_list:
            local = random.sample(in_list, 2)
            for i in local:
                in_list.remove(i)
            self.groups_of_two.append(local)

    def divide_breeding_mut_cross(self, in_list, percentage_crossover):
        """
            Based on the percentage crossover we separate the breeding list
            to a list with chromosomes for crossover and a list with chromosomes
            for mutation. If the percentage is 0.8 and the breeding population
            is 100 the 80 chromosomes will be selected for crossover and the rest
            20 for mutation.
        """
        total = len(in_list)
        amount_for_crossover = int(total * percentage_crossover)
        self.population_for_crossover = random.sample(in_list, amount_for_crossover)
        self.population_for_mutation = [x for x in in_list if x not in self.population_for_crossover]

    def one_point_crossover(self, in_list):
        """
            Given the list of chromosomes we first create random pairs of doubles
            and the we apply a simple point crossover by choosing a random point in
            the operator is going to take place
        """
        local_children = []
        self.random_pick_doubles(in_list)
        local_doubles = self.groups_of_two
        while local_doubles:
            double = local_doubles.pop()
            ind1 = double[0][1]
            ind2 = double[1][1]
            size = min(len(ind1), len(ind2))
            cxpoint = random.randint(1, size - 1)
            child1 = ind1[cxpoint:] + ind2[:cxpoint]
            child2 = ind2[cxpoint:] + ind1[:cxpoint]
            local_children.append(child1)
            local_children.append(child2)
        return local_children

    def remove_duplicate_cities(self, in_list):
        """
            The offsprings from the crossover contain duplicate cities which must
            be removed by replacing them with cities that are not in the the child
        """
        for dirty in in_list:
            differs = [x for x in self.tour_init if x not in dirty]
            doubles = [x for x, y in collections.Counter(dirty).items() if y > 1]
            for double in doubles:
                local_dirty = dirty[:]
                cleaned_distances_list = []
                local_cleaned = []
                indexes = [i for i, x in enumerate(dirty) if
                           x == double]  # for the duplicate value those are the indexes we can find it in the list
                for index in indexes:
                    for different in differs:
                        del local_dirty(index)
                        local_dirty.insert(index, different)
                        local_cleaned.append(local_dirty)
            print len(local_cleaned)
            for cleaned in local_cleaned:
                doubles1 = [x for x, y in collections.Counter(cleaned).items() if y > 1]
                print doubles1
                cleaned_distance = TSPDistance(cleaned, self.city_coords)
                cleaned_distances_list.append((cleaned_distance.distance_cost, cleaned_distance.tourlist))
                local_temp = sorted(cleaned_distances_list, key=lambda x: x[0])
                cleaned_path = []
                cleaned_shortest_path_cost = min(i[0] for i in local_temp)
                for i in local_temp:
                    if i[0] == cleaned_shortest_path_cost:
                        cleaned_path = (i[1])
            self.offsprings.append(cleaned_path)