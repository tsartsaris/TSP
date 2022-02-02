from typing import List, Dict

import numpy as np

from events_handler.events import EventsHandler, EventTypes, SubscriberRole
from tsp_solver.helpers_s import calculate_distance


class Solver:
    initial_population = []
    basic_chromosome: List = []
    problem_dict: Dict

    @classmethod
    def __init__(cls):
        EventsHandler.subscribe(event_type=EventTypes.SOLVE,
                                subscriber_role=SubscriberRole.LISTENER,
                                fn=cls.on_start_solving)

    @classmethod
    def on_start_solving(cls, data):
        cls.problem_dict = EventsHandler.dispatch_data(event_type=EventTypes.TSP_DATA_REQUEST, data=Dict)
        cls.create_initial_chromosome(dict_data=cls.problem_dict)
        # print(list(dict_data.values()))
        # dt = np.dtype('float,float')
        #
        # vals =  np.array(list(dict_data.values()), dt)
        # for x in range(10):
        #     ran = np.random.permutation(vals)
        #     cls.initial_routes.append(ran)
        #
        # EventsHandler.post_event(event_type=EventTypes.PLOT_REQUEST, data=ran)
        # print(calculate_distance(ran))

    @classmethod
    def create_initial_chromosome(cls, dict_data: Dict):
        list_of_cities = list(dict_data.keys())
        cls.basic_chromosome = list_of_cities + list(list_of_cities[0])
        print(cls.basic_chromosome)
        cls.plot_chromosome(cls.basic_chromosome)
        cls.create_initial_population(10)

    @classmethod
    def create_initial_population(cls, amount: int):
        """
        Taking a initial chromosome of type [1,2,3,4,5,1]
        take the subset excluding start and end (1)
        and shuffle them
        :param amount: number of initial population to create
        :return: NADA assign to initial_population
        """
        start_end_city = cls.basic_chromosome[0]
        chromosome_subset = np.array(cls.basic_chromosome[1:-1])
        for i in range(amount):
            inner_permutation = np.random.permutation(chromosome_subset)
            complete_permutation = [start_end_city] + list(inner_permutation) + [start_end_city]
            cls.initial_population.append(complete_permutation)
        print(cls.initial_population)

    @classmethod
    def plot_chromosome(cls, data):
        cities_to_plot = [cls.problem_dict[x] for x in data]
        EventsHandler.post_event(event_type=EventTypes.PLOT_REQUEST, data=cities_to_plot)
