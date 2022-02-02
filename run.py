"""
Main entry point
"""

from plotty.plotter import Plotter
from tsp_solver.solver import Solver
from tsp_ui.main_window import MainWindow
from tsp_solver.parser import TSPParser

TSPParser()
Plotter()
Solver()

if __name__ == "__main__":
    window = MainWindow()
    window.run()
