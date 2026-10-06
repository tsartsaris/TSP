# -*- coding: utf-8 -*-
"""
Recreate the figures used in the README:

    python docs/make_figures.py

Every run is seeded, so the figures come out the same each time. Reading this
script is also a good example of using the modules without the GUI.
"""

import os
import random
import sys

import matplotlib
matplotlib.use("Agg")  # draw to files, no window
import matplotlib.pyplot as plt
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tsp_ga import GeneticAlgorithm  # noqa: E402  (needs the path above)
from tsp_ga_init_pop import create_initial_population, nearest_neighbour_tour  # noqa: E402
from tsp_parser import read_tour_file, read_tsp_file  # noqa: E402

PROBLEMS = os.path.join(ROOT, "TSP_Problems")
IMAGES = os.path.join(ROOT, "docs", "images")

# colours: chart surface, text, muted axes, two series
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#898781", "#e1e0d9"
BLUE, ORANGE = "#2a78d6", "#eb6834"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "font.size": 10,
})


def load(name):
    problem = read_tsp_file(os.path.join(PROBLEMS, name + ".tsp"))
    optimal_tour = read_tour_file(os.path.join(PROBLEMS, name + ".opt.tour"))
    return problem, optimal_tour


def draw_tour(axes, problem, tour, title, color=BLUE):
    xs, ys = zip(*problem.tour_coordinates(tour + tour[:1]))
    axes.plot(xs, ys, "-", color=color, linewidth=1.5)
    axes.plot(xs, ys, "o", color=INK, markersize=3)
    axes.set_title(title, fontsize=10)
    axes.set_xticks([])
    axes.set_yticks([])
    axes.set_aspect("equal")


def run_ga(problem, population, mode, generations, seed, crossover=0.9):
    """Run the GA and return it plus the best length after every generation."""
    random.seed(seed)
    ga = GeneticAlgorithm(problem, create_initial_population(problem, population, mode), crossover)
    history = [ga.best_length]
    for _ in range(generations):
        ga.step()
        history.append(ga.best_length)
    return ga, history


def tours_figure():
    """Random tour -> nearest neighbour -> genetic algorithm -> optimal, on berlin52."""
    problem, optimal = load("berlin52")
    random.seed(1)
    random_tour = random.sample(problem.cities, len(problem.cities))
    greedy = nearest_neighbour_tour(problem, 1)
    ga, _ = run_ga(problem, 100, "shuffle", 300, seed=4)

    figure, axes = plt.subplots(1, 4, figsize=(14, 3.6))
    for ax, tour, title in [
        (axes[0], random_tour, "Random tour"),
        (axes[1], greedy, "Nearest neighbour"),
        (axes[2], ga.best_tour, "Genetic algorithm, 300 generations"),
        (axes[3], optimal, "Optimal (TSPLIB)"),
    ]:
        draw_tour(ax, problem, tour, "%s\nlength %d" % (title, problem.tour_length(tour)))
    figure.tight_layout()
    figure.savefig(os.path.join(IMAGES, "tours.png"), dpi=110, bbox_inches="tight")
    plt.close(figure)


def convergence_figure():
    """Best tour length per generation on bier127, for both initial population modes."""
    problem = read_tsp_file(os.path.join(PROBLEMS, "bier127.tsp"))
    optimal_length = 118282  # published by TSPLIB; there is no bier127.opt.tour file
    generations = 3000
    figure, axes = plt.subplots(figsize=(9, 4.5))
    finals = {}
    for mode, color in [("shuffle", BLUE), ("elitism", ORANGE)]:
        _, history = run_ga(problem, 100, mode, generations, seed=11)
        axes.plot(history, color=color, linewidth=2, label=mode)
        finals[mode] = history[-1]
    # label the end of each line; the higher line's label goes above, the other below
    higher = max(finals, key=finals.get)
    for mode, final in finals.items():
        axes.annotate("%s  %d" % (mode, final), (generations, final), xytext=(6, 7 if mode == higher else -7),
                      textcoords="offset points", va="center", color=INK)
    axes.axhline(optimal_length, color=MUTED, linewidth=1, linestyle="--")
    axes.annotate("optimal  %d" % optimal_length, (generations, optimal_length), xytext=(6, -10),
                  textcoords="offset points", va="center", color=MUTED)
    axes.set_ylim(optimal_length * 0.95, 200000)  # random starts are ~390000, cut off to show the end
    axes.set_xlim(0, generations)
    axes.set_xlabel("Generation")
    axes.set_ylabel("Best tour length")
    axes.set_title("bier127: best tour per generation (population 100)", loc="left")
    axes.grid(True, color=GRID, linewidth=0.8)
    axes.spines[["top", "right"]].set_visible(False)
    axes.legend(frameon=False, loc="upper right")
    figure.tight_layout()
    figure.savefig(os.path.join(IMAGES, "convergence.png"), dpi=110, bbox_inches="tight")
    plt.close(figure)


def evolution_gif():
    """Animated GIF of the best tour on a280 improving over the generations."""
    problem, _ = load("a280")
    random.seed(21)
    ga = GeneticAlgorithm(problem, create_initial_population(problem, 100, "elitism"), 0.9)
    frames = []
    snapshot_at = set(range(0, 3001, 75))
    figure, axes = plt.subplots(figsize=(6, 4.6))
    for generation in range(3001):
        if generation in snapshot_at:
            axes.clear()
            draw_tour(axes, problem, ga.best_tour, "a280  generation %d  length %d" % (generation, ga.best_length))
            figure.tight_layout()
            figure.canvas.draw()
            frames.append(Image.frombytes("RGBA", figure.canvas.get_width_height(),
                                          bytes(figure.canvas.buffer_rgba())).convert("P", palette=Image.ADAPTIVE))
        ga.step()
    plt.close(figure)
    durations = [150] * (len(frames) - 1) + [2500]  # hold the last frame
    frames[0].save(os.path.join(IMAGES, "evolution.gif"), save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, optimize=True)


if __name__ == "__main__":
    os.makedirs(IMAGES, exist_ok=True)
    tours_figure()
    convergence_figure()
    evolution_gif()
    print("figures written to", IMAGES)
