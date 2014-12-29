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


matplotlib.use('TkAgg')


root = Tk()
root.title("TSP Solver")
root.geometry("1024x768")

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

    current_tour_distance = TSPDistance(newtsp.city_tour_init, newtsp.city_coords)
    text_distance.config(state=NORMAL)
    text_distance.delete('1.0', '2.0')
    text_distance.insert('1.0', current_tour_distance.distance_cost)
    text_distance.config(state=DISABLED)



button1 = ttk.Button(root, text='Open TSP file', padding=5, command=openfile)
label_distance = ttk.Label(root, text="Current distance:", background='lightgreen', font=('times', 12, 'bold'))
label_distance.grid(row=0, column=2, sticky=(W, N, S, E))

text_distance = Text(root, width=10, height=1, bg='lightgreen', fg="red", font=('times', 12, 'bold'))
button1.grid(row=0, column=1, sticky=W)
text_distance.grid(row=0, column=3, sticky=(W, N, S, E))

root.mainloop()