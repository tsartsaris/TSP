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

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from tsp_parser import *
from tsp_ga_init_pop import *
from tsp_ga import *


root = Tk()
root.title("TSP Solver")
root.geometry("1024x768")


class VisualSolve:
    def __init__(self, master):
        self.temp = []
        self.local_temp = []
        self.best_tour = []
        self.master = master
        self.newtsp = []
        self.init_plot(master)
        self.frame = Frame(master)
        self.frame = Frame(width=150, height=500, bg="lightblue", bd=1, relief=SUNKEN)
        self.frame.grid(row=1, column=2, columnspan=2, rowspan=2, sticky=(E, W, N, S))
        self.button_open_tsp_file = ttk.Button(master, text='Open TSP file', command=self.openfile)
        self.button_open_tsp_file.grid(row=0, column=1, sticky=W)
        self.add_distance_visual_element(master)

    def init_plot(self, master):
        """
            Create an empty initial plot to instantiate the GUI layout
        """
        f = Figure(figsize=(8, 6), dpi=100)
        a = f.add_subplot(111)
        a.plot(10, 10)
        a.set_title('Current tour plot')
        a.set_xlabel('X axis coordinates')
        a.set_ylabel('Y axis coordinates')
        canvas = FigureCanvasTkAgg(f, master)
        canvas.show()
        canvas.get_tk_widget().grid(row=1, column=1, sticky=W)


    def add_distance_visual_element(self, master):
        label_distance = ttk.Label(master, text="Current distance:", background='lightgreen',
                                   font=('times', 12, 'bold'))
        label_distance.grid(row=0, column=2, sticky=(W, N, S, E))
        # this get changed from update_current_visual_distance
        self.text_distance = Text(master, width=10, height=1, bg='lightgreen', fg="red", font=('times', 12, 'bold'))
        self.text_distance.grid(row=0, column=3, sticky=(W, N, S, E))

    def create_initial_population_visual_element(self):
        var = StringVar(self.frame)
        var.set("shuffle")  # initial value
        label_distance = ttk.Label(self.frame, text="Select mode:", background='lightgreen', font=('times', 12, 'bold'))
        label_distance.grid(row=0, column=0, sticky=(W, N, S))
        option1 = OptionMenu(self.frame, var, "shuffle", "elitism")
        option1.grid(row=0, column=1, sticky=(W, N, S))
        button = Button(self.frame, text="Create initial population", pady=5,
                        command=lambda: self.create_initial_population_button(var.get()))
        button.grid(row=1, column=0, columnspan=2, sticky=(E, W, N, S))

    def openfile(self, frame1=None):
        """
            This is called when the button button_open_tsp_file is pressed
            it opens the tkinter file dialog , passes the selected file to
            the parser class and process as needed.
        """
        filename = tkFileDialog.askopenfilename()
        self.newtsp = TSPParser(filename)
        print self.newtsp.display_status

        # from this line to the end of else we check if there is an error on the parser
        # if there is an error we display it, else we parse the file normally and we
        # plot the instance of the problem
        if self.newtsp.display_status:
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
            text_error.insert('1.0', self.newtsp.display_status)
            text_error.config(state=DISABLED)
        else:
            if frame1:
                frame1.destroy()
            frame1 = Frame(width=400, height=50, bg="lightgreen", bd=1, relief=SUNKEN)
            frame1.grid(row=2, column=1, sticky=W)
            label_distance1 = ttk.Label(frame1, text="File opened:", background="lightgreen",
                                        font=('times', 12, 'bold'))
            label_distance1.grid(row=0, column=0, sticky=W)
            text_error = Text(frame1, width=85, height=1, bg='lightgreen', fg="blue", font=('times', 12, 'bold'))
            text_error.grid(row=0, column=1, sticky=(W, N, S, E))
            text_error.config(state=NORMAL)
            text_error.delete('1.0', '2.0')
            text_error.insert('1.0', self.newtsp.filename)
            text_error.config(state=DISABLED)

            self.plot_tour(self.newtsp.city_tour_tuples)
            self.init_tour = self.newtsp.city_tour_init
            self.city_coords = self.newtsp.city_coords


            self.current_tour_distance = TSPDistance(self.newtsp.city_tour_init, self.newtsp.city_coords)
            self.update_visual_current_distance(self.current_tour_distance.distance_cost)
            self.create_initial_population_visual_element()

    def plot_tour(self, tour_tuples):
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

    def update_visual_current_distance(self, distance):
        """
            Each time we want to update the distance on the GUI
            we call this passing the distance as parameter
        """
        self.text_distance.config(state=NORMAL)
        self.text_distance.delete('1.0', '2.0')
        self.text_distance.insert('1.0', distance)
        self.text_distance.config(state=DISABLED)

    def create_initial_population_button(self, type):
        self.new_pop = self.create_init_pop(self.city_coords, self.init_tour, type)
        # after the initial population created we evaluate the distances to see if we have
        # a better solution than the one loaded with the parser
        distances_list = []  # here we will store locally tuples of distance cost and tours
        for elem in self.new_pop:
            loc_dist = TSPDistance(elem, self.city_coords)
            distances_list.append((loc_dist.distance_cost, loc_dist.tourlist))
        self.temp = sorted(distances_list, key=lambda x: x[0])
        shortest_path = []
        shortest_path_distance_cost = min(i[0] for i in self.temp)

        for i in self.temp:
            if i[0] == shortest_path_distance_cost:
                shortest_path = (i[1])
        shortest_path_tuples = []
        for city in shortest_path:
            shortest_path_tuples.append(self.city_coords.get(city))
        self.best_tour.append((shortest_path_distance_cost, shortest_path))
        self.update_visual_current_distance(shortest_path_distance_cost)
        self.plot_tour(shortest_path_tuples)
        button1 = Button(self.frame, text="Create children", pady=3, command=lambda: self.create_offsprings_round_one())
        button1.grid(row=3, column=0, columnspan=2, sticky=(E, W, N, S))


    def create_init_pop(self, init_dict, init_tour, type):
        """
            We create the initial population with TSPInitialPopulation class
            we pass the dict with cities and coordinates and the initial tour
        """
        new_pop = TSPInitialPopulation(init_dict, init_tour, 100,
                                       type)  # plus the population initial size (here is 200)
        return new_pop.pop_group

    def create_offsprings_round_one(self):
        tsp_ga_solve = TSPGeneticAlgo(self.temp, self.init_tour, self.best_tour[0])
        offspring_distances_list = []
        for offspring in tsp_ga_solve.offsprings:
            offspring_distance = TSPDistance(offspring, self.city_coords)
            offspring_distances_list.append((offspring_distance.distance_cost, offspring_distance.tourlist))
        self.local_temp = sorted(offspring_distances_list, key=lambda x: x[0])
        while len(self.local_temp) > 100:
            self.local_temp.pop()
        offspring_shortest_path = []
        offspring_shortest_path_cost = min(i[0] for i in self.local_temp)
        if offspring_shortest_path_cost < self.best_tour[0][0]:
            for i in self.local_temp:
                if i[0] == offspring_shortest_path_cost:
                    offspring_shortest_path = (i[1])
            self.best_tour[:] = []
            self.best_tour.append((offspring_shortest_path_cost, offspring_shortest_path))
            offspring_shortest_path_tuples = []
            for city in offspring_shortest_path:
                offspring_shortest_path_tuples.append(self.city_coords.get(city))

            self.update_visual_current_distance(offspring_shortest_path_cost)
            self.plot_tour(offspring_shortest_path_tuples)
        button2 = Button(self.frame, text="Start genetic algorithm", pady=3, command=lambda: self.start_solving())
        button2.grid(row=4, column=0, columnspan=2, sticky=(E, W, N, S))
        return self

    def start_solving(self):
        for i in range(2000):
            circle = circleGA(self.temp, self.local_temp, self.init_tour, self.best_tour[0], self.city_coords)
            children_distances_list = []
            children_distances_list[:] = []
            for child in circle.offsprings:
                child_distance = TSPDistance(child, self.city_coords)
                children_distances_list.append((child_distance.distance_cost, child_distance.tourlist))
            self.local_temp[:] = []
            self.local_temp = sorted(children_distances_list, key=lambda x: x[0])
            while len(self.local_temp) > 100:
                self.local_temp.pop()
            children_shortest_path = []
            children_shortest_path[:] = []
            children_shortest_path_cost = min(i[0] for i in self.local_temp)
            print children_shortest_path_cost
            if children_shortest_path_cost < self.best_tour[0][0]:
                for i in self.local_temp:
                    if i[0] == children_shortest_path_cost:
                        children_shortest_path = (i[1])
                self.best_tour[:] = []
                self.best_tour.append((children_shortest_path_cost, children_shortest_path))
                children_shortest_path_tupples = []
                children_shortest_path_tupples[:] = []
                for city in children_shortest_path:
                    children_shortest_path_tupples.append(self.city_coords.get(city))
                self.update_visual_current_distance(children_shortest_path_cost)
                self.plot_tour(children_shortest_path_tupples)



b = VisualSolve(root)
root.mainloop()