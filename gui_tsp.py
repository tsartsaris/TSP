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
from tsp_ga import *


matplotlib.use('TkAgg')
init_tour = []  # the tour got from the TSP data file
new_pop = []  # the initial population based on the above tour
city_coords = []
root = Tk()
root.title("TSP Solver")
root.geometry("1024x768")


def init_plot():
    """
        Create an empty initial plot to instantiate the GUI layout
    """
    f = Figure(figsize=(8, 6), dpi=100)
    a = f.add_subplot(111)
    a.plot(10, 10)
    a.set_title('Current tour plot')
    a.set_xlabel('X axis coordinates')
    a.set_ylabel('Y axis coordinates')
    canvas = FigureCanvasTkAgg(f, master=root)
    canvas.show()
    canvas.get_tk_widget().grid(row=1, column=1, sticky=W)


init_plot()

global shortest_path_cost


def openfile(frame1=None):
    filename = tkFileDialog.askopenfilename()
    newtsp = TSPParser(filename)
    if newtsp.display_status:
        if frame1:
            frame1.destroy()
        frame1 = Frame(width=400, height=50, bg="red", bd=1, relief=SUNKEN)
        frame1.grid(row=2, column=1, sticky=W)
        label_distance1 = ttk.Label(frame1, text="Error:", background='red', font=('times', 12, 'bold'))
        label_distance1.grid(row=0, column=0, sticky=W)
        text_error = Text(frame1, width=90, height=1, bg='black', fg="red", font=('times', 12, 'bold'))
        text_error.grid(row=0, column=1, sticky=(W, N, S, E))
        text_error.config(state=NORMAL)
        text_error.delete('1.0', '2.0')
        text_error.insert('1.0', newtsp.display_status)
        text_error.config(state=DISABLED)
    else:
        if frame1:
            frame1.destroy()
        frame1 = Frame(width=400, height=50, bg="lightgreen", bd=1, relief=SUNKEN)
        frame1.grid(row=2, column=1, sticky=W)
        label_distance1 = ttk.Label(frame1, text="File opened:", background="lightgreen", font=('times', 12, 'bold'))
        label_distance1.grid(row=0, column=0, sticky=W)
        text_error = Text(frame1, width=85, height=1, bg='lightgreen', fg="blue", font=('times', 12, 'bold'))
        text_error.grid(row=0, column=1, sticky=(W, N, S, E))
        text_error.config(state=NORMAL)
        text_error.delete('1.0', '2.0')
        text_error.insert('1.0', newtsp.filename)
        text_error.config(state=DISABLED)

    plot_tour(newtsp.city_tour_tuples)
    init_tour = newtsp.city_tour_init
    city_coords = newtsp.city_coords

    current_tour_distance = TSPDistance(newtsp.city_tour_init, newtsp.city_coords)
    update_visual_current_distance(current_tour_distance.distance_cost)
    temp = []

    def create_initial_population_button(type):
        new_pop = create_init_pop(newtsp.city_coords, init_tour, type)
        distances_list = []

        for elem in new_pop:
            loc_dist = TSPDistance(elem, newtsp.city_coords)

            distances_list.append((loc_dist.distance_cost, loc_dist.tourlist))
        temp = map(sorted, distances_list)
        shortest_path = []
        global shortest_path_distance_cost
        shortest_path_distance_cost = min(i[0] for i in temp)

        for i in temp:
            if i[0] == shortest_path_distance_cost:
                shortest_path = (i[1])
        shortest_path_tuples = []
        for city in shortest_path:
            shortest_path_tuples.append(newtsp.city_coords.get(city))

        update_visual_current_distance(shortest_path_distance_cost)
        plot_tour(shortest_path_tuples)


    var = StringVar(frame)
    var.set("shuffle")  # initial value
    label_distance = ttk.Label(frame, text="Select mode:", background='lightgreen', font=('times', 12, 'bold'))
    label_distance.grid(row=0, column=0, sticky=(W, N, S))
    option1 = OptionMenu(frame, var, "shuffle", "elitism")
    option1.grid(row=0, column=1, sticky=(W, N, S))
    button = Button(frame, text="Create initial population", pady=5,
                    command=lambda: create_initial_population_button(var.get()))
    button.grid(row=1, column=0, columnspan=2, sticky=(E, W, N, S))
    button1 = Button(frame, text="Create children", pady=3, command=lambda: create_offsprings_rone(init_tour))
    button1.grid(row=3, column=0, columnspan=2, sticky=(E, W, N, S))
    button2 = Button(frame, text="Start genetic algorithm", pady=3, command=lambda: start_solving)
    button2.grid(row=4, column=0, columnspan=2, sticky=(E, W, N, S))


    def create_offsprings_rone(city_tour_init):
        tsp_ga_solve = TSPGeneticAlgo(temp, city_tour_init)
        offspring_distances_list = []
        for offspring in tsp_ga_solve.offsprings:
            offspring_distance = TSPDistance(offspring, city_coords)
            offspring_distances_list.append((offspring_distance.distance_cost, offspring_distance.tourlist))
        local_temp = map(sorted, offspring_distances_list)
        offspring_shortest_path = []
        offspring_shortest_path_cost = min(i[0] for i in local_temp)
        if offspring_shortest_path_cost < shortest_path_distance_cost:
            shortest_path_distance_cost = offspring_shortest_path_cost
            for i in local_temp:
                if i[0] == offspring_shortest_path_cost:
                    offspring_shortest_path = (i[1])
            shortest_path = offspring_shortest_path
            offspring_shortest_path_tuples = []
            for city in shortest_path:
                offspring_shortest_path_tuples.append(city_coords.get(city))

            update_visual_current_distance(shortest_path_cost)
            plot_tour(offspring_shortest_path_tuples)


    def start_solving():
        def circle1(temp1, local_temp1):
            temp = temp1
            local_temp = local_temp1
            offspring_distances_list = []
            circle = circleGA(temp, local_temp)
            circle.recursion_circle_output()

            local_initial_population = circle.clear_all_pop()
            for offspring in local_initial_population:
                offspring_distance = TSPDistance(offspring, city_coords)
                offspring_distances_list.append((offspring_distance.distance_cost, offspring_distance.tourlist))
            local_temp = map(sorted, offspring_distances_list)
            offspring_shortest_path = []
            offspring_shortest_path_cost = min(i[0] for i in local_temp)
            print offspring_shortest_path_cost
            if offspring_shortest_path_cost < shortest_path_cost:
                shortest_path_cost = offspring_shortest_path_cost
                for i in local_temp:
                    if i[0] == offspring_shortest_path_cost:
                        offspring_shortest_path = (i[1])
                shortest_path = offspring_shortest_path
                offspring_shortest_path_tuples = []
                for city in shortest_path:
                    offspring_shortest_path_tuples.append(city_coords.get(city))

                update_visual_current_distance(shortest_path_cost)
                plot_tour(offspring_shortest_path_tuples)

            local_children = circle.create_new_children()
            for offspring in local_children:
                offspring_distance = TSPDistance(offspring, city_coords)
                offspring_distances_list.append((offspring_distance.distance_cost, offspring_distance.tourlist))
            temp = map(sorted, offspring_distances_list)
            offspring_shortest_path = []
            offspring_shortest_path_cost = min(i[0] for i in temp)
            print offspring_shortest_path_cost
            if offspring_shortest_path_cost < shortest_path_cost:
                shortest_path_cost = offspring_shortest_path_cost
                for i in temp:
                    if i[0] == offspring_shortest_path_cost:
                        offspring_shortest_path = (i[1])
                shortest_path = offspring_shortest_path
                offspring_shortest_path_tuples = []
                for city in shortest_path:
                    offspring_shortest_path_tuples.append(city_coords.get(city))

                update_visual_current_distance(shortest_path_cost)
                plot_tour(offspring_shortest_path_tuples)

        for i in range(50):
            circle1(temp, local_temp)


    def create_init_pop(init_dict, init_tour, type):
        """
            We create the initial population with TSPInitialPopulation class
            we pass the dict with cities and coordinates and the initial tour
        """
        new_pop = TSPInitialPopulation(init_dict, init_tour, 50,
                                       type)  # plus the population initial size (here is 50)
        return new_pop.pop_group


def update_visual_current_distance(distance):
    """
        Each time we want to update the distance on the GUI
        we call this passing the distance as parameter
    """
    text_distance.config(state=NORMAL)
    text_distance.delete('1.0', '2.0')
    text_distance.insert('1.0', distance)
    text_distance.config(state=DISABLED)


def plot_tour(tour_tuples):
    """
        We call this passing the list of tuples with city
        coordinates to plot the tour we want on the GUI
    """
    f = Figure(figsize=(8, 6), dpi=100)
    a = f.add_subplot(111)
    a.scatter(*zip(*tour_tuples))
    a.plot(*zip(*tour_tuples))
    a.set_title('Current best tour')
    a.set_xlabel('X axis coordinates')
    a.set_ylabel('Y axis coordinates')

    canvas = FigureCanvasTkAgg(f, master=root)
    canvas.show()
    canvas.get_tk_widget().grid(row=1, column=1, sticky=W)


# visual elements
button1 = ttk.Button(root, text='Open TSP file', command=openfile)
button1.grid(row=0, column=1, sticky=W)

label_distance = ttk.Label(root, text="Current distance:", background='lightgreen', font=('times', 12, 'bold'))
label_distance.grid(row=0, column=2, sticky=(W, N, S, E))
# this get changed from update_current_visual_distance
text_distance = Text(root, width=10, height=1, bg='lightgreen', fg="red", font=('times', 12, 'bold'))
text_distance.grid(row=0, column=3, sticky=(W, N, S, E))
# a frame to hold some elements aside of the plot area to avoid stretching
frame = Frame(width=150, height=500, bg="lightblue", bd=1, relief=SUNKEN)
frame.grid(row=1, column=2, columnspan=2, rowspan=2, sticky=(E, W, N, S))



# initiate the GUI
root.mainloop()