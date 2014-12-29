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

from Tkinter import *
import tkFileDialog
import ttk

import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from tsp_distance import *
from tsp_parser import *
from tsp_ga_init_pop import *


matplotlib.use('TkAgg')
init_tour = []
new_pop = []
root = Tk()
root.title("TSP Solver")
root.geometry("1024x768")
f = Figure(figsize=(8, 6), dpi=100)
a = f.add_subplot(111)
a.plot(10, 10)
a.set_title('Current tour plot')
a.set_xlabel('X axis coordinates')
a.set_ylabel('Y axis coordinates')
canvas = FigureCanvasTkAgg(f, master=root)
canvas.show()
canvas.get_tk_widget().grid(row=1, column=1, sticky=W)

def openfile():
    filename = tkFileDialog.askopenfilename()
    newtsp = TSPParser(filename)
    print newtsp.city_coords
    f = Figure(figsize=(8, 6), dpi=100)
    a = f.add_subplot(111)

    a.scatter(*zip(*newtsp.city_tour_tuples))
    a.plot(*zip(*newtsp.city_tour_tuples))
    a.set_title('Current tour plot')
    a.set_xlabel('X axis coordinates')
    a.set_ylabel('Y axis coordinates')


    # a tk.DrawingArea
    canvas = FigureCanvasTkAgg(f, master=root)
    canvas.show()
    canvas.get_tk_widget().grid(row=1, column=1, sticky=W)
    init_tour = newtsp.city_tour_init
    current_tour_distance = TSPDistance(newtsp.city_tour_init, newtsp.city_coords)
    text_distance.config(state=NORMAL)
    text_distance.delete('1.0', '2.0')
    text_distance.insert('1.0', current_tour_distance.distance_cost)
    text_distance.config(state=DISABLED)
    create_init_pop(init_tour)


def create_init_pop(init_tour):
    new_pop = TSPInitialPopulation(init_tour, 50)
    print new_pop.pop_group



button1 = ttk.Button(root, text='Open TSP file', padding=5, command=openfile)
label_distance = ttk.Label(root, text="Current distance:", background='lightgreen', font=('times', 12, 'bold'))
label_distance.grid(row=0, column=2, sticky=(W, N, S, E))

text_distance = Text(root, width=10, height=1, bg='lightgreen', fg="red", font=('times', 12, 'bold'))
button1.grid(row=0, column=1, sticky=W)
text_distance.grid(row=0, column=3, sticky=(W, N, S, E))
frame = Frame(width=100, height=576, bg="lightblue", bd=1, relief=SUNKEN, padx=10)
frame.grid(row=1, column=2, sticky=E)
label_distance1 = ttk.Label(frame, text="Current distance:", background='lightblue', font=('times', 12, 'bold'))
label_distance1.grid(row=1, column=0, sticky=E)
label_distance2 = ttk.Label(frame, text="Current distance:", background='lightblue', font=('times', 12, 'bold'))
label_distance2.grid(row=2, column=0, sticky=E)
root.mainloop()