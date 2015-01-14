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
import copy

from tsp_distance import *


class TSPGeneticAlgo(object):
    def __init__(self, initial_population, city_tour_init, total_best):
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

        # self.tournament_selection(self.all_fitness)
        self.best_selection()
        for each in self.selected_for_breeding:
            self.offsprings.append(each[1])
            # print self.selected_for_breeding
            # self.divide_breeding_mut_cross(self.selected_for_breeding,
            # 0)  # produces population for crossover and mutation
            # self.children_dirty = self.one_point_crossover(self.population_for_crossover)
            # self.remove_duplicate_cities(self.children_dirty)
            # #self.mutate_elitism()
            # for each in self.population_for_mutation:
            #     self.offsprings.append(each[1])

    def fitness_function(self, city_cost):
        """
            We apply the fitness function to each distance by
            dividing the lowest with each one of them
        """
        return round(float(float(self.total_best) / float(city_cost)), 7)

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
        if len(in_list)%2 != 0:
            in_list.pop()
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

    def pmx_crossover(self, in_list):
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
            mom = double[0][1]
            dad = double[1][1]
            size = len(mom)
            points = random.sample(range(size), 2)
            x, y = min(points), max(points)
            bro = copy.copy(dad)
            bro[x:y + 1] = mom[x:y + 1]
            sis = copy.copy(mom)
            sis[x:y + 1] = dad[x:y + 1]
            for parent, child in zip([dad, mom], [bro, sis]):
                for i in range(x, y + 1):
                    if parent[i] not in child[x:y + 1]:
                        spot = i
                        while x <= spot <= y:
                            spot = parent.index(child[spot])
                        child[spot] = parent[i]
            local_children.append(bro)
            local_children.append(sis)
        return local_children

    def best_selection(self):
        self.selected_for_breeding = self.all_fitness  # [:len(self.all_fitness) / 2]

    def remove_duplicate_cities(self, in_list):
        """
            The offsprings from the crossover contain duplicate cities which must
            be removed by replacing them with cities that are not in the offspring
        """
        for dirty in in_list:
            # coin = random.randint(1, 10)
            # if coin == 1:
            self.random_cities = []
            self.random_cities[:] = []
            self.differs = [x for x in self.tour_init if x not in dirty]
            uniq = [x for x, y in collections.Counter(dirty).items() if y > 1]
            if self.differs and uniq:
                coin = random.randint(0, 3)
                if coin == 0:
                    self.random_remaining_cities = self.differs[:]
                    for unique in uniq:
                        index = dirty.index(unique)
                        dirty.pop(index)
                    city = self.pick_random_city()
                    best_nn_tour = self.create_nearest_tour(city)
                    dirty = dirty + best_nn_tour
                elif coin == 1:
                    self.random_remaining_cities = self.differs[:]
                    for unique in uniq:
                        index = dirty.index(unique)
                        dirty.pop(index)
                    city = self.pick_random_city()
                    best_nn_tour = self.create_nearest_tour(city)
                    dirty = best_nn_tour + dirty
                elif coin == 2:
                    self.random_remaining_cities = self.differs[:]
                    for unique in uniq:
                        index = dirty.index(unique)
                        dirty.pop(index)
                    city = self.pick_random_city()
                    best_nn_tour = self.create_nearest_tour(city)
                    randominsert = random.randint(1, len(dirty) - 1)
                    dirty = dirty[:randominsert] + best_nn_tour + dirty[randominsert:]
                else:
                    for unique in uniq:
                        index = dirty.index(unique)
                        dirty.pop(index)
                        dirty.insert(index, self.differs[-1])
                        self.differs.pop()

            self.offsprings.append(dirty)  # at this point we have all the children from the crossover operation
                # cleaned from duplicates in the self.offsprings list
            # else:
            # differs = [x for x in self.tour_init if x not in dirty]
            #     uniq = [x for x, y in collections.Counter(dirty).items() if y > 1]
            #
            # self.offsprings.append(dirty)  # at this point we have all the children from the crossover operation
                # cleaned from duplicates in the self.offsprings list

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
        return self.city_coords.get(city)


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
        prov_list = self.differs[:]
        nearest_tour = [city]
        if city in prov_list: prov_list.remove(city)
        while prov_list:
            current_city = nearest_tour[-1]
            next_city = self.find_nn(current_city, prov_list)
            nearest_tour.append(next_city[1])
            prov_list.remove(next_city[1])
        return nearest_tour


    @staticmethod
    def insertion_mutation(in_list):
        tour_range = len(in_list)
        randominsert = random.randint(0, tour_range - 1)
        randomip = random.randint(0, tour_range - 1)
        city_to_insert = in_list.pop(randomip)
        in_list.insert(randominsert, city_to_insert)
        return in_list

    @staticmethod
    def reciprocal_exchange_mutation(in_list):
        a = random.randint(0, len(in_list) - 1)
        b = random.randint(0, len(in_list) - 1)
        in_list[b], in_list[a] = in_list[a], in_list[b]
        return in_list

    @staticmethod
    def two_opt_mutation(in_list):
        a = random.randint(0, len(in_list) - 2)
        b = a + 1
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

    @staticmethod
    def inverse(in_list):
        in_list.reverse()
        return in_list


    def mutate_elitism(self):
        for tour in self.population_for_mutation:
            coin = random.randint(1, 3)
            if coin == 1:
                mutated = self.insertion_mutation(tour[1])
                self.offsprings.append(mutated)
            elif coin == 2:
                mutated = self.reciprocal_exchange_mutation(tour[1])
                self.offsprings.append(mutated)
            else:
                mutated = self.inversion_mutation(tour[1])
                self.offsprings.append(mutated)


class circleGA(TSPGeneticAlgo):
    def __init__(self, temp, local_temp, city_tour_init, total_best, city_coords, pop_size, p):
        self.prop = p
        self.rpopsize = pop_size
        if self.prop == 1:
            self.mutsize = 1
        else:
            self.mutsize = self.rpopsize - self.rpopsize * self.prop
        self.children_dirty = []
        self.groups_of_two = []
        self.population_for_crossover = []
        self.population_for_mutation = []
        self.children_dirty[:] = []
        self.groups_of_two[:] = []
        self.population_for_crossover[:] = []
        self.population_for_mutation[:] = []
        self.offsprings = []
        self.offsprings[:] = []
        self.temp = temp

        self.local_temp = local_temp
        self.tour_init = city_tour_init
        self.total_best = total_best[0]
        self.city_coords = city_coords
        self.pre_temp = []
        self.entire_population = []
        self.all_fitness = []
        self.all_fitness[:] = []
        self.initial_population = []
        self.initial_population[:] = []
        self.selected_for_breeding = []  # here we store the population selected from the tournament selection
        self.selected_for_breeding[:] = []
        self.add_init_offsprings()
        self.calculate_fitness(self.entire_population)
        self.all_fitness_temp = []
        self.all_fitness_temp[:] = self.all_fitness
        # num = random.randint(1,2)
        # if num == 1:
        #self.tournament_selection(self.all_fitness)
        # else:
        self.best_selection()
        self.complete_initial_exchanged_population()
        self.normalize_initial_population()
        self.initial_population[:] = self.temp
        self.selected_for_breeding[:] = []
        self.calculate_fitness(self.initial_population)
        # num = random.randint(1,2)
        # if num == 1:
        #self.tournament_selection(self.all_fitness)
        # else:
        self.best_selection()
        self.divide_breeding_mut_cross(self.selected_for_breeding,
                                       self.prop)  # produces population for crossover and mutation
        crosscoin = random.randint(0, 4)
        if crosscoin == 0:
            self.children_dirty = self.pmx_crossover(self.population_for_crossover)
        else:
            self.children_dirty = self.one_point_crossover(self.population_for_crossover)

        self.remove_duplicate_cities(self.children_dirty)
        self.complete_population_for_mutation()
        self.normalise_lists(self.population_for_mutation)
        self.mutate_elitism()
        self.fin()




    def add_init_offsprings(self):
        self.entire_population[:] = []
        self.entire_population = self.temp + self.local_temp
        self.entire_population = sorted(self.entire_population, key=lambda x: x[0])
        self.entire_population = self.entire_population[:self.rpopsize]


    def complete_initial_exchanged_population(self):
        while len(self.selected_for_breeding) < self.rpopsize:
            tour_to_add = random.choice(self.all_fitness_temp)
            if tour_to_add not in self.selected_for_breeding:
                self.selected_for_breeding.append(tour_to_add)

    def complete_population_for_mutation(self):
        if len(self.population_for_mutation) > self.mutsize:
            while len(self.population_for_mutation) != self.mutsize:
                todel = random.choice(self.population_for_mutation)
                self.population_for_mutation.remove(todel)
        else:
            while len(self.population_for_mutation) != self.mutsize:
                toadd = random.choice(self.all_fitness_temp)
                coin = random.randint(0, 3)
                if coin == 0:
                    mutated = self.inversion_mutation(toadd)
                    self.population_for_mutation.append(mutated)
                elif coin == 2:
                    mutated = self.insertion_mutation(toadd)
                    self.population_for_mutation.append(mutated)
                elif coin == 1:
                    mutated = self.reciprocal_exchange_mutation(toadd)
                    self.population_for_mutation.append(mutated)
                else:
                    mutated = self.two_opt_mutation(toadd)
                    self.population_for_mutation.append(mutated)

    def normalize_initial_population(self):
        for each in self.selected_for_breeding:
            self.pre_temp.append(each[1])
        pre_temp_distances_list = []
        for offspring in self.pre_temp:
            offspring_distance = TSPDistance(offspring, self.city_coords)
            pre_temp_distances_list.append((offspring_distance.distance_cost, offspring_distance.tourlist))
        self.temp = sorted(pre_temp_distances_list, key=lambda x: x[0])

    @staticmethod
    def normalise_lists(in_list):
        for eachone in in_list:
            if type(eachone[1]) == float:
                eachone.reverse()

    def fin(self):
        self.initial_population[:] = []
        self.initial_population = sorted(self.temp, key=lambda x: x[0])
        return self.initial_population