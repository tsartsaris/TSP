# -*- coding: utf-8 -*-
"""
The genetic algorithm.

A genetic algorithm (GA) imitates natural evolution. It keeps a *population*
of candidate solutions, here tours, and improves it generation after generation:

    1. Selection   the best tours survive, the worst are dropped
    2. Crossover   pairs of surviving tours (parents) are combined into children
    3. Mutation    other survivors are copied with a small random change
    4. Repeat with the survivors and the new children

The length of a tour plays the role of *fitness*: the shorter, the fitter.

Tours need special operators. A tour is a *permutation*: every city must appear
exactly once. Cutting two parents and gluing the pieces together (classic
one-point crossover) usually breaks that rule, so this module shows both ways of
dealing with it: one-point crossover followed by a *repair* step, and two
crossovers designed to always produce valid permutations, PMX and OX.

Run this file directly to solve a problem without the GUI:

    python tsp_ga.py TSP_Problems/berlin52.tsp --generations 2000
"""

__author__ = "Tsartsaris Sotiris"
__copyright__ = "Copyright 2014, The TSP Project"
__license__ = "APACHE 2.0"

import random
from collections import Counter
from operator import itemgetter

from tsp_ga_init_pop import nearest_neighbour_tour

# The crossovers a pair of parents can be bred with, and the default share of
# pairs (in percent) that use each one. See GeneticAlgorithm.crossover_mix.
# Half one-point, half OX was the best mix in docs/compare_crossovers.py.
CROSSOVER_ONE_POINT = "one-point"
CROSSOVER_PMX = "pmx"
CROSSOVER_OX = "ox"
CROSSOVERS = (CROSSOVER_ONE_POINT, CROSSOVER_PMX, CROSSOVER_OX)
DEFAULT_CROSSOVER_MIX = {CROSSOVER_ONE_POINT: 50, CROSSOVER_PMX: 0, CROSSOVER_OX: 50}


# ---------------------------------------------------------------------------
# Crossover: combine two parent tours into two children
# ---------------------------------------------------------------------------

def one_point_crossover(parent_a, parent_b):
    """
        Cut both parents at the same random point and swap the tails:

            parent_a  [1 2 3 | 4 5 6]        child_1  [1 2 3 | 6 2 5]
            parent_b  [4 1 3 | 6 2 5]   ->   child_2  [4 1 3 | 4 5 6]

        The children usually visit some cities twice and miss others
        (child_1 above has 2 twice and no 4), so they must be repaired.
    """
    point = random.randint(1, len(parent_a) - 1)
    return parent_a[:point] + parent_b[point:], parent_b[:point] + parent_a[point:]


def repair(child, problem):
    """
        Turn a child that visits some cities twice into a valid tour.

        Most of the time (3 in 4) one copy of each duplicated city is
        removed and the missing cities are joined into a nearest neighbour
        fragment, which is added at the start, the end or a random position.
        The greedy fragment carries useful local structure into the child.

        Otherwise each duplicate is simply replaced by one of the missing cities.
    """
    present = set(child)
    missing = [city for city in problem.cities if city not in present]
    if not missing:
        return child  # already a valid tour

    duplicates = [city for city, count in Counter(child).items() if count > 1]
    child = child[:]
    choice = random.randrange(4)
    if choice == 3:
        for city in duplicates:
            child[child.index(city)] = missing.pop()
        return child

    for city in duplicates:
        del child[child.index(city)]
    fragment = nearest_neighbour_tour(problem, random.choice(missing), missing)
    if choice == 0:
        return child + fragment
    if choice == 1:
        return fragment + child
    position = random.randint(0, len(child))
    return child[:position] + fragment + child[position:]


def _pmx_child(segment_parent, other_parent, start, end):
    """
        Build one PMX child: the segment [start, end] comes from segment_parent,
        every other position from other_parent, then conflicts are resolved by
        following the mapping between the two segments.
    """
    child = other_parent[:]
    child[start:end + 1] = segment_parent[start:end + 1]
    segment = set(child[start:end + 1])
    position_in_other = {city: index for index, city in enumerate(other_parent)}

    for i in range(start, end + 1):
        city = other_parent[i]
        if city in segment:
            continue  # this city is already in the child, inside the copied segment
        # city was overwritten by the segment and now lacks a place. Follow the
        # mapping (the city that replaced it -> where that city sits in
        # other_parent) until we land outside the segment: that place is free.
        spot = i
        while start <= spot <= end:
            spot = position_in_other[child[spot]]
        child[spot] = city
    return child


def pmx_crossover(parent_a, parent_b):
    """
        Partially Mapped Crossover (PMX, Goldberg & Lingle 1985).

        A random segment is copied from one parent, the remaining positions
        are filled from the other parent, and cities that would appear twice
        are swapped using the mapping between the two segments:

            parent_a  [1 2 | 3 4 5 | 6 7]
            parent_b  [3 7 | 5 1 6 | 4 2]
            child     [6 7 | 3 4 5 | 1 2]   segment of a, rest from b, mapping 3->5->6, 4->1

        Every child is a valid tour without needing any repair.
    """
    start, end = sorted(random.sample(range(len(parent_a)), 2))
    return (_pmx_child(parent_a, parent_b, start, end),
            _pmx_child(parent_b, parent_a, start, end))


def _ox_child(segment_parent, other_parent, start, end):
    """
        Build one OX child: keep the segment [start, end] of segment_parent in
        place, then fill the free positions, starting right after the segment
        and wrapping around, with the other parent's remaining cities in the
        order they appear in other_parent (also read from right after the segment).
    """
    size = len(segment_parent)
    child = [None] * size
    child[start:end + 1] = segment_parent[start:end + 1]
    segment = set(child[start:end + 1])
    # other_parent read from just after the segment, wrapping around to the start
    order = [other_parent[(end + 1 + i) % size] for i in range(size)]
    remaining = iter(city for city in order if city not in segment)
    for i in range(size - (end - start + 1)):
        child[(end + 1 + i) % size] = next(remaining)
    return child


def order_crossover(parent_a, parent_b):
    """
        Order Crossover (OX, Davis 1985).

        A random segment is copied from one parent. The other cities keep the
        *relative order* they have in the other parent, which suits the TSP:
        what matters in a tour is which city follows which, not absolute positions.

            parent_a  [1 2 3 | 4 5 6 | 7 8 9]
            parent_b  [9 3 7 | 8 2 6 | 5 1 4]
            child     [7 8 2 | 4 5 6 | 1 9 3]

        parent_b read from after the segment is 5 1 4 9 3 7 8 2 6. Dropping the
        segment's cities 4 5 6 leaves 1 9 3 7 8 2. These fill the child starting
        after the segment (1 9 3) and wrapping around to the front (7 8 2).
        Every child is a valid tour.
    """
    start, end = sorted(random.sample(range(len(parent_a)), 2))
    return (_ox_child(parent_a, parent_b, start, end),
            _ox_child(parent_b, parent_a, start, end))


# ---------------------------------------------------------------------------
# Mutation: a small random change to one tour. Each returns a new list and
# leaves the parent untouched; changing the parent in place would silently
# corrupt a tour that is still in the population with its old length.
# ---------------------------------------------------------------------------

def insertion_mutation(tour):
    """Move one random city to a random new position: [1 2 3 4 5] -> [1 3 4 2 5]"""
    tour = tour[:]
    city = tour.pop(random.randrange(len(tour)))
    tour.insert(random.randrange(len(tour) + 1), city)
    return tour


def swap_mutation(tour):
    """Swap two random cities, also called reciprocal exchange: [1 2 3 4 5] -> [1 4 3 2 5]"""
    tour = tour[:]
    a, b = random.randrange(len(tour)), random.randrange(len(tour))
    tour[a], tour[b] = tour[b], tour[a]
    return tour


def inversion_mutation(tour):
    """
        Reverse a random segment: [1 2 3 4 5 6] -> [1 5 4 3 2 6]

        This is the most useful mutation for the TSP. Reversing a segment
        replaces just two edges of the tour (it is the "2-opt" move), so it can
        untangle two crossing edges without disturbing the rest of the tour.
    """
    a, b = sorted(random.sample(range(len(tour) + 1), 2))
    return tour[:a] + tour[a:b][::-1] + tour[b:]


MUTATIONS = (insertion_mutation, swap_mutation, inversion_mutation)


# ---------------------------------------------------------------------------
# The algorithm
# ---------------------------------------------------------------------------

class GeneticAlgorithm:
    """
        Evolves a population of tours for a TSPProblem, one generation per
        call to step(). The best tour found so far is always in best_tour and
        best_length.
    """

    def __init__(self, problem, initial_tours, crossover_probability=0.9, crossover_mix=None):
        """
            initial_tours          the first generation, see tsp_ga_init_pop
            crossover_probability  share of the survivors bred by crossover; the
                                   rest are mutated. 0.9 is a common choice.
            crossover_mix          percentage of the crossover pairs bred with each
                                   crossover, e.g. {"one-point": 50, "pmx": 0, "ox": 50};
                                   DEFAULT_CROSSOVER_MIX when not given
        """
        self.problem = problem
        self.population_size = len(initial_tours)
        self.crossover_probability = crossover_probability
        self.crossover_mix = crossover_mix or DEFAULT_CROSSOVER_MIX
        self.generation = 0
        # The population is kept as (length, tour) pairs so every tour is
        # measured only once.
        self.population = self._evaluate(initial_tours)
        self.children = []
        self.best_length, self.best_tour = self.population[0]

    @property
    def crossover_mix(self):
        return dict(zip(CROSSOVERS, self._crossover_weights))

    @crossover_mix.setter
    def crossover_mix(self, mix):
        """Accept percentages that add up to 100; crossovers left out get 0."""
        unknown = set(mix) - set(CROSSOVERS)
        if unknown:
            raise ValueError("Unknown crossover %s, use %s" % (", ".join(sorted(unknown)), ", ".join(CROSSOVERS)))
        weights = [mix.get(name, 0) for name in CROSSOVERS]
        if any(weight < 0 for weight in weights) or sum(weights) != 100:
            raise ValueError("Crossover percentages must not be negative and must add up to 100, got %s" % mix)
        self._crossover_weights = weights

    def _crossover(self, parent_a, parent_b):
        """
            Breed two children, choosing the crossover at random with the
            crossover_mix percentages as weights.
        """
        name = random.choices(CROSSOVERS, weights=self._crossover_weights)[0]
        if name == CROSSOVER_PMX:
            return pmx_crossover(parent_a, parent_b)
        if name == CROSSOVER_OX:
            return order_crossover(parent_a, parent_b)
        return [repair(child, self.problem) for child in one_point_crossover(parent_a, parent_b)]

    def _evaluate(self, tours):
        """(length, tour) for every tour, shortest first."""
        return sorted(((self.problem.tour_length(tour), tour) for tour in tours), key=itemgetter(0))

    def _select_survivors(self, candidates):
        """
            The population_size shortest tours among candidates, each tour only once.

            Dropping duplicates matters more than it looks. Without it, copies of
            the current best tour soon fill the whole population, every parent is
            the same tour and the search gets stuck ("premature convergence").
            On berlin52 this one check is the difference between stalling around
            8000 and reaching the optimal 7542.
        """
        survivors = []
        seen = set()
        for length, tour in sorted(candidates, key=itemgetter(0)):
            if tuple(tour) in seen:
                continue
            seen.add(tuple(tour))
            survivors.append((length, tour))
            if len(survivors) == self.population_size:
                break
        return survivors

    def step(self):
        """
            Run one generation. Returns True when it found a new best tour.
        """
        # 1. Selection. Parents and children compete together and only the
        #    best population_size survive. Because the best tour always
        #    survives, the result can never get worse ("elitist" selection).
        self.population = self._select_survivors(self.population + self.children)

        # 2. Split the survivors at random: a share crossover_probability is
        #    bred by crossover, the others are mutated.
        parents = [tour for _, tour in self.population]
        random.shuffle(parents)
        crossover_count = int(len(parents) * self.crossover_probability)
        crossover_parents, mutation_parents = parents[:crossover_count], parents[crossover_count:]
        if not mutation_parents:
            mutation_parents = [random.choice(parents)]  # always mutate at least one tour

        # 3. Crossover: pair the parents up (0 with 1, 2 with 3, ...), each pair
        #    bred with a crossover picked according to crossover_mix.
        children = []
        for parent_a, parent_b in zip(crossover_parents[0::2], crossover_parents[1::2]):
            children.extend(self._crossover(parent_a, parent_b))

        # 4. Mutation: each remaining parent gets one randomly chosen mutation.
        for parent in mutation_parents:
            mutate = random.choice(MUTATIONS)
            children.append(mutate(parent))

        # The children join the competition at the start of the next generation.
        self.children = self._evaluate(children)
        self.generation += 1

        if self.children and self.children[0][0] < self.best_length:
            self.best_length, self.best_tour = self.children[0]
            return True
        return False


def _main():
    """Solve a problem from the command line and print the progress."""
    import argparse
    import time

    from tsp_ga_init_pop import INIT_MODES, create_initial_population
    from tsp_parser import read_tsp_file

    parser = argparse.ArgumentParser(description="Solve a TSPLIB problem with the genetic algorithm.")
    parser.add_argument("tsp_file", help="a TSPLIB .tsp file, e.g. TSP_Problems/berlin52.tsp")
    parser.add_argument("--population", type=int, default=100, help="population size (default 100)")
    parser.add_argument("--generations", type=int, default=1000, help="number of generations (default 1000)")
    parser.add_argument("--crossover", type=float, default=0.9, help="crossover probability (default 0.9)")
    parser.add_argument("--init", choices=INIT_MODES, default="elitism", help="initial population (default elitism)")
    mix_group = parser.add_argument_group(
        "crossover mix", "Percent of the crossover pairs bred with each crossover, adding up to 100. "
                         "Once any is given, the others count as 0. Default: %s."
                         % ", ".join("%s %d" % item for item in DEFAULT_CROSSOVER_MIX.items()))
    for name in CROSSOVERS:
        mix_group.add_argument("--" + name, type=int, metavar="PERCENT")
    parser.add_argument("--seed", type=int, help="random seed, to make a run repeatable")
    args = parser.parse_args()

    given = {name: getattr(args, name.replace("-", "_")) for name in CROSSOVERS}
    if all(percent is None for percent in given.values()):
        mix = DEFAULT_CROSSOVER_MIX
    else:
        mix = {name: percent or 0 for name, percent in given.items()}
    if sum(mix.values()) != 100:
        parser.error("the crossover percentages must add up to 100, got %s" % mix)

    random.seed(args.seed)
    problem = read_tsp_file(args.tsp_file)
    started = time.time()
    ga = GeneticAlgorithm(problem, create_initial_population(problem, args.population, args.init),
                          args.crossover, mix)
    print("%s: %d cities, best initial tour %d" % (problem.name, len(problem.cities), ga.best_length))
    for _ in range(args.generations):
        if ga.step():
            print("generation %5d  best %d" % (ga.generation, ga.best_length))
    print("best tour length %d after %d generations in %.1fs" % (ga.best_length, ga.generation, time.time() - started))


if __name__ == "__main__":
    _main()
