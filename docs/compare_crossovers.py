# -*- coding: utf-8 -*-
"""
Compare crossover mixes, as in the README's "Comparing the crossovers" table:

    python docs/compare_crossovers.py

Every mix gets the same time budget on each problem, repeated with a few random
seeds. The result is the average gap between the best tour found and the known
optimum (lower is better). With the defaults it takes about 9 minutes; use
--seconds and --runs to trade time for accuracy.
"""

import argparse
import os
import random
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tsp_ga import GeneticAlgorithm  # noqa: E402  (needs the path above)
from tsp_ga_init_pop import create_initial_population  # noqa: E402
from tsp_parser import read_tsp_file  # noqa: E402

OPTIMAL_LENGTHS = {"berlin52": 7542, "bier127": 118282, "a280": 2579}  # published by TSPLIB
MIXES = {
    "one-point 100%": {"one-point": 100},
    "PMX 100%": {"pmx": 100},
    "OX 100%": {"ox": 100},
    "one-point/PMX 80/20": {"one-point": 80, "pmx": 20},
    "one-point/OX 50/50": {"one-point": 50, "ox": 50},
    "equal 34/33/33": {"one-point": 34, "pmx": 33, "ox": 33},
}


def main():
    parser = argparse.ArgumentParser(description="Compare crossover mixes on a few TSPLIB problems.")
    parser.add_argument("--seconds", type=float, default=10, help="time budget per run (default 10)")
    parser.add_argument("--runs", type=int, default=3, help="runs per mix and problem (default 3)")
    parser.add_argument("--population", type=int, default=100, help="population size (default 100)")
    args = parser.parse_args()

    print("%-20s %s" % ("mix", "  ".join("%9s" % name for name in OPTIMAL_LENGTHS)))
    problems = {name: read_tsp_file(os.path.join(ROOT, "TSP_Problems", name + ".tsp")) for name in OPTIMAL_LENGTHS}
    for label, mix in MIXES.items():
        gaps = []
        for name, problem in problems.items():
            run_gaps = []
            for seed in range(1, args.runs + 1):
                random.seed(seed)  # the same seeds for every mix, so every mix gets the same start
                tours = create_initial_population(problem, args.population, "elitism")
                ga = GeneticAlgorithm(problem, tours, 0.9, mix)
                stop_at = time.time() + args.seconds
                while time.time() < stop_at:
                    ga.step()
                run_gaps.append(100.0 * (ga.best_length - OPTIMAL_LENGTHS[name]) / OPTIMAL_LENGTHS[name])
            gaps.append(statistics.mean(run_gaps))
        print("%-20s %s" % (label, "  ".join("%8.1f%%" % gap for gap in gaps)), flush=True)


if __name__ == "__main__":
    main()
