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
from collections import deque


class TSPGeneticAlgo:
    def __init__(self, initial_population, city_tour_init, total_best):
        self.city_tour_init = city_tour_init  # pass the initial tour here for differences between children after crossover duplicates
        self.children_dirty = []
        self.total_best = total_best[0]
        print self.total_best
        self.offsprings = []
        self.children = []
        self.all_fitness = []
        self.groups_of_two = []
        self.population_for_mutation = []
        self.initial_population = initial_population
        self.selected_population = []
        self.calculate_fitness(self.initial_population)
        self.sorted_all_fintess()
        self.accumulated_list = self.accumulate_fitness()
        for i in range(50):
            self.selected_population.append(self.roulette_wheel_selection())
        print self.selected_population
        self.random_pick_doubles(self.selected_population)
        self.children_dirty = self.crossover_genetic_operator(self.groups_of_two)
        self.remove_duplicate_cities(self.children_dirty)
        self.mutate_pop()

    def fitness_function(self, city_cost):
        """
            We apply the fitness function to each distance by
            dividing the lowest with each one of them
        """
        return round(float(float(self.total_best) / float(city_cost)), 3)

    def select_best_pop(self, accumulated_list):
        accumulated_list = accumulated_list[::-1]
        print accumulated_list
        best = accumulated_list[150:]
        rand = random.sample(accumulated_list, 50)
        accumulated_list = best + rand
        return accumulated_list


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

    def sorted_all_fintess(self):
        self.sorted_fitness = sorted(self.all_fitness, key=itemgetter(0))


    def roulette_wheel_selection(self):
        """
            iterating a range we get each time a random number from 0 to 1
            then we iterate the sorted list of accumulated fitness values and we get
             the first higher from that number not removing it from the list
             allowing each chromosome to be a parent more than once
        """
        max = sum(element[0] for element in self.sorted_fitness)
        pick = random.uniform(0, max)
        current = 0
        for element in self.sorted_fitness:
            current += element[0]
            if current > pick:
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
        """
            Takes the pairs of chromosomes in the list and applies a crossover
            on a random point to create offsprings.
        """
        local_doubles = []
        local_children = []
        for double in in_list:
            if isinstance(double[0][1], (list, tuple)):
                local_doubles.append(double[0][1])
            if isinstance(double[1][1], (list, tuple)):
                local_doubles.append(double[1][1])
        local_doubles = map(None, *[iter(local_doubles)] * 2)
        local_doubles_for_crossover = random.sample(local_doubles, len(local_doubles) / 2)
        for pair in local_doubles_for_crossover:
            local_doubles.remove(pair)
            ind1 = pair[0]
            ind2 = pair[1]
            size = min(len(ind1), len(ind2))
            cxpoint = random.randint(1, size - 1)
            ind1[cxpoint:], ind2[cxpoint:] = ind2[cxpoint:], ind1[cxpoint:]
            local_children.append(ind1)
            local_children.append(ind2)
        for pop in local_doubles:
            self.population_for_mutation.append(pop[0])
            self.population_for_mutation.append(pop[1])
        return local_children

    def remove_duplicate_cities(self, in_list):
        """
            The offsprings from the crossover contain duplicate cities which must
            be removed by replacing them with cities that are not in the the child
        """
        for dirty in in_list:
            differs = [x for x in self.city_tour_init if x not in dirty]
            uniq = [x for x, y in collections.Counter(dirty).items() if y > 1]
            for unique in uniq:
                index = dirty.index(unique)
                dirty.pop(index)
                dirty.insert(index, differs[-1])
                differs.pop()
            self.offsprings.append(dirty)
            self.children.append(dirty)

    def mutate_pop(self):
        self.i = 1
        self.population_for_mutation_half_1 = self.population_for_mutation[:len(self.population_for_mutation) / 2]
        self.population_for_mutation_half_2 = self.population_for_mutation[len(self.population_for_mutation) / 2:]
        for i in self.population_for_mutation_half_1:
            a = random.randint(1, len(self.population_for_mutation))
            b = random.randint(1, len(self.population_for_mutation))
            i[b], i[a] = i[a], i[b]
        for lis in self.population_for_mutation_half_2:
            lis = deque(lis)
            lis.rotate(self.i)
            self.i += 1
        self.population_for_mutation = self.population_for_mutation_half_1 + self.population_for_mutation_half_2
        self.offsprings = self.offsprings + self.population_for_mutation
        return self.offsprings


class circleGA(TSPGeneticAlgo):
    def __init__(self, initial_population, children_population, total_best, tour_init):
        self.children_dirty = []
        self.children = []
        self.offsprings = []
        self.all_fitness = []
        self.groups_of_two = []
        self.population_for_mutation = []
        self.selected_population = []
        self.initial_population_c = initial_population
        self.children_population_c = children_population
        self.city_tour_init = tour_init
        self.total_best = total_best
        self.current_best = self.current_best_score(self.children_population_c)
        if self.current_best < self.total_best:
            self.total_best = self.current_best

    def recursion_circle_output(self):
        self.all_pop = self.children_population_c + self.initial_population_c
        self.current_best = self.current_best_score(self.all_pop)
        if self.current_best < self.total_best:
            self.total_best = self.current_best
        self.calculate_fitness(self.all_pop)
        self.sorted_all_fintess()
        self.accumulated_list = self.accumulate_fitness()
        for i in range(50):
            self.selected_population.append(self.roulette_wheel_selection())
            # _self.selected_population = self.select_best_pop(self.sorted_fitness)
            # for i in range(50):
            # self.selected_population.append(self.roulette_wheel_selection(self.accumulated_list))


    def clear_all_pop(self):
        self.all_pop = []
        for selected in self.selected_population:
            self.all_pop.append(selected[1])
        return self.all_pop

    def create_new_children(self):
        self.random_pick_doubles(self.selected_population)
        self.children_dirty = self.crossover_genetic_operator(self.groups_of_two)
        self.remove_duplicate_cities(self.children_dirty)
        self.mutate_children()
        return self.children

    def mutate_children(self):
        self.i = 1
        self.offsprings_half = self.children[:len(self.children) / 2]
        self.offsprings_half_1 = self.children[len(self.children) / 2:]
        for i in self.offsprings_half:
            a = random.randint(1, len(self.offsprings_half))
            b = random.randint(1, len(self.offsprings_half))
            i[b], i[a] = i[a], i[b]
        for lis in self.offsprings_half_1:
            lis = deque(lis)
            lis.rotate(self.i)
            self.i += 1
        self.children = self.offsprings_half + self.offsprings_half_1
        temp = self.children
        self.children = temp[-1:] + temp[1:-1] + temp[:1]
        print len(self.children)
        return self.children
