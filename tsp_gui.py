# -*- coding: utf-8 -*-
"""
Tkinter GUI for the genetic algorithm.

    python tsp_gui.py

Open a TSPLIB problem, create the initial population and start the algorithm.
The plot shows the best tour found so far and is redrawn whenever it improves.

How the GUI stays responsive: Tkinter can only redraw the window and react to
clicks while its event loop (mainloop) is free. Instead of running all the
generations in one long loop, which would freeze the window, the GUI runs
generations for a few milliseconds, updates the display and then asks Tkinter
to call it again with root.after(). Everything happens in Tkinter's own thread,
which is the safe way to drive a Tkinter interface.
"""

__author__ = "Tsartsaris Sotiris"
__copyright__ = "Copyright 2014, The TSP Project"
__license__ = "APACHE 2.0"

import os
import time
import tkinter as tk
from tkinter import filedialog, ttk

import matplotlib
matplotlib.use("TkAgg")  # must be chosen before anything else from matplotlib draws
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from tsp_ga import GeneticAlgorithm
from tsp_ga_init_pop import INIT_MODES, create_initial_population
from tsp_parser import TSPFileError, read_tour_file, read_tsp_file

PROBLEMS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "TSP_Problems")
TIME_SLICE_SECONDS = 0.05  # how long to compute before letting Tkinter redraw the window
REDRAW_SECONDS = 0.5       # redraw the plot at most this often; drawing is slower than a generation


class TSPSolverApp:
    """The main window: a tour plot on the left and the controls on the right."""

    def __init__(self, root):
        self.root = root
        self.problem = None          # the loaded TSPProblem
        self.optimal_length = None   # known optimum, if a .opt.tour file sits next to the problem
        self.ga = None               # the GeneticAlgorithm, created by "Create initial population"
        self.running = False
        self.last_generation = 0     # the generation at which the current run stops
        self.plot_outdated = False   # a better tour was found but isn't drawn yet
        self.last_drawn = 0.0        # time.perf_counter() of the last plot redraw

        root.title("TSP Solver")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self._build_plot()
        self._build_controls()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_plot(self):
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.canvas.mpl_connect("motion_notify_event", self._show_mouse_coordinates)
        self.mouse_label = ttk.Label(self.root, text=" ", anchor="w")
        self.mouse_label.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 6))
        self._draw(None, "Open a TSP file to start")

    def _build_controls(self):
        panel = ttk.Frame(self.root, padding=10)
        panel.grid(row=0, column=1, rowspan=2, sticky="ns")
        bold = ("TkDefaultFont", 10, "bold")

        # Step 1: the problem
        ttk.Button(panel, text="Open TSP file...", command=self.open_file).grid(row=0, column=0, columnspan=2, sticky="ew")
        self.file_label = ttk.Label(panel, text="No file loaded", wraplength=220)
        self.file_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 12))

        # Step 2: the initial population
        ttk.Label(panel, text="Initial population", font=bold).grid(row=2, column=0, columnspan=2, sticky="w")
        ttk.Label(panel, text="Mode").grid(row=3, column=0, sticky="w")
        self.mode = tk.StringVar(value="elitism")
        ttk.Combobox(panel, textvariable=self.mode, values=INIT_MODES, state="readonly", width=10).grid(row=3, column=1, sticky="e")
        ttk.Label(panel, text="Population size").grid(row=4, column=0, columnspan=2, sticky="w")
        self.population_size = tk.Scale(panel, from_=20, to=1000, resolution=10, orient=tk.HORIZONTAL)
        self.population_size.set(100)
        self.population_size.grid(row=5, column=0, columnspan=2, sticky="ew")
        self.create_button = ttk.Button(panel, text="Create initial population", command=self.create_population, state=tk.DISABLED)
        self.create_button.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(4, 12))

        # Step 3: the genetic algorithm
        ttk.Label(panel, text="Genetic algorithm", font=bold).grid(row=7, column=0, columnspan=2, sticky="w")
        ttk.Label(panel, text="Generations to run").grid(row=8, column=0, columnspan=2, sticky="w")
        self.generations = tk.Scale(panel, from_=100, to=10000, resolution=100, orient=tk.HORIZONTAL)
        self.generations.set(2000)
        self.generations.grid(row=9, column=0, columnspan=2, sticky="ew")
        ttk.Label(panel, text="Crossover probability").grid(row=10, column=0, columnspan=2, sticky="w")
        self.crossover = tk.Scale(panel, from_=0.1, to=1.0, resolution=0.1, orient=tk.HORIZONTAL)
        self.crossover.set(0.9)
        self.crossover.grid(row=11, column=0, columnspan=2, sticky="ew")
        self.start_button = ttk.Button(panel, text="Start", command=self.start, state=tk.DISABLED)
        self.start_button.grid(row=12, column=0, sticky="ew", pady=4)
        self.stop_button = ttk.Button(panel, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_button.grid(row=12, column=1, sticky="ew", pady=4)

        # Results
        ttk.Label(panel, text="Results", font=bold).grid(row=13, column=0, columnspan=2, sticky="w", pady=(12, 0))
        self.result_labels = {}
        for row, name in enumerate(("Generation", "Best distance", "Optimal distance", "Gap to optimal"), start=14):
            ttk.Label(panel, text=name).grid(row=row, column=0, sticky="w")
            self.result_labels[name] = ttk.Label(panel, text="-", font=bold)
            self.result_labels[name].grid(row=row, column=1, sticky="e")

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _draw(self, tour, title):
        """
            Plot the cities of a tour, joined in visiting order and back to the
            start. GEO problems store (latitude, longitude); they are drawn with
            longitude across so the map isn't rotated.
        """
        self.axes.clear()
        self.axes.set_title(title)
        self.axes.grid(True)
        if self.problem is not None:
            points = self.problem.tour_coordinates(tour or self.problem.cities)
            if self.problem.edge_weight_type == "GEO":
                points = [(lon, lat) for lat, lon in points]
                self.axes.set_xlabel("Longitude")
                self.axes.set_ylabel("Latitude")
            else:
                self.axes.set_xlabel("X")
                self.axes.set_ylabel("Y")
            xs, ys = zip(*points)
            if tour:
                # repeat the first city at the end to draw the edge back to the start
                self.axes.plot(xs + xs[:1], ys + ys[:1], "-", color="tab:blue", linewidth=1)
            self.axes.plot(xs, ys, "o", color="tab:red", markersize=4)
        self.canvas.draw_idle()

    def _show_mouse_coordinates(self, event):
        if event.inaxes:
            self.mouse_label.config(text="x = %.1f   y = %.1f" % (event.xdata, event.ydata))

    def _show_results(self):
        self.result_labels["Generation"].config(text=str(self.ga.generation))
        self.result_labels["Best distance"].config(text=str(self.ga.best_length))
        if self.optimal_length:
            gap = 100.0 * (self.ga.best_length - self.optimal_length) / self.optimal_length
            self.result_labels["Gap to optimal"].config(text="%.1f%%" % gap)

    def _draw_best(self):
        self.plot_outdated = False
        self.last_drawn = time.perf_counter()
        self._draw(self.ga.best_tour, "%s: best tour %d (generation %d)"
                   % (self.problem.name, self.ga.best_length, self.ga.generation))

    # ------------------------------------------------------------------
    # Button actions
    # ------------------------------------------------------------------

    def open_file(self):
        path = filedialog.askopenfilename(initialdir=PROBLEMS_FOLDER, filetypes=[("TSPLIB problems", "*.tsp"), ("All files", "*")])
        if not path:
            return  # the dialog was cancelled
        self.stop()
        try:
            problem = read_tsp_file(path)
        except (TSPFileError, OSError, ValueError) as error:
            self.file_label.config(text="Error: %s" % error, foreground="red")
            return

        self.problem, self.ga = problem, None
        self.file_label.config(text="%s, %d cities, %s" % (problem.name, len(problem.cities), problem.edge_weight_type),
                               foreground="")
        # A known optimal tour next to the problem lets us show how close we get.
        tour_path = os.path.splitext(path)[0] + ".opt.tour"
        self.optimal_length = problem.tour_length(read_tour_file(tour_path)) if os.path.exists(tour_path) else None
        for label in self.result_labels.values():
            label.config(text="-")
        if self.optimal_length:
            self.result_labels["Optimal distance"].config(text=str(self.optimal_length))
        self._draw(None, "%s: %d cities" % (problem.name, len(problem.cities)))
        self.create_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)

    def create_population(self):
        self.stop()
        tours = create_initial_population(self.problem, self.population_size.get(), self.mode.get())
        self.ga = GeneticAlgorithm(self.problem, tours, self.crossover.get())
        self._show_results()
        self._draw_best()
        self.start_button.config(state=tk.NORMAL)

    def start(self):
        """Run the chosen number of generations, continuing from where the last run stopped."""
        self.running = True
        self.last_generation = self.ga.generation + self.generations.get()
        self.start_button.config(state=tk.DISABLED)
        self.create_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self._run_time_slice()

    def stop(self):
        """Stop after the generation in progress; the best tour stays on the plot."""
        self.running = False
        if self.plot_outdated:
            self._draw_best()
        self.stop_button.config(state=tk.DISABLED)
        if self.problem is not None:
            self.create_button.config(state=tk.NORMAL)
        if self.ga is not None:
            self.start_button.config(state=tk.NORMAL)

    def _run_time_slice(self):
        """
            Run generations for TIME_SLICE_SECONDS, update the display, then
            schedule the next slice. Returning to Tkinter between slices keeps
            the window responsive and lets the Stop button be clicked.
        """
        if not self.running:
            return
        self.ga.crossover_probability = self.crossover.get()  # the slider can be moved during a run
        deadline = time.perf_counter() + TIME_SLICE_SECONDS
        while time.perf_counter() < deadline and self.ga.generation < self.last_generation:
            if self.ga.step():
                self.plot_outdated = True
        self._show_results()
        finished = self.ga.generation >= self.last_generation
        if self.plot_outdated and (finished or time.perf_counter() - self.last_drawn >= REDRAW_SECONDS):
            self._draw_best()
        if finished:
            self.stop()
        else:
            self.root.after(1, self._run_time_slice)


def main():
    root = tk.Tk()
    TSPSolverApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
