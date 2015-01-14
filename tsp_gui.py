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
import threading

import matplotlib
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from tsp_parser import *
from tsp_ga_init_pop import *
from tsp_ga import *


matplotlib.use('TkAgg')
root = Tk()
root.title("TSP Solver")
root.geometry("1024x768")

text_cx = Label(root, bg='black', fg="white", width=1, font=('times', 12, 'bold'))
text_cx.grid(row=6, column=1, sticky=(W, N, S, E))
text_cy = Label(root, bg='black', fg="white", font=('times', 12, 'bold'))
text_cy.grid(row=7, column=1, sticky=(W, N, S, E))


def on_move(event):
    # get the x and y pixel coords
    x, y = event.x, event.y

    if event.inaxes:
        ax = event.inaxes  # the axes instance
        text_cx.config(text='data coords X %f' % (round(event.xdata, 1)))
        text_cy.config(text='data coords Y %f' % (round(event.ydata, 1)))


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
        b = Figure(figsize=(8, 6), dpi=100)
        ac = b.add_subplot(111)
        ac.plot(10, 10)
        ac.set_title('Current tour plot')
        ac.set_xlabel('X axis coordinates')
        ac.set_ylabel('Y axis coordinates')
        ac.grid(True)
        canvas = FigureCanvasTkAgg(b, master)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=1, sticky=W)


    def add_distance_visual_element(self, master):
        label_distance = ttk.Label(master, text="Current distance:", background='lightgreen',
                                   font=('times', 12, 'bold'))
        label_distance.grid(row=0, column=2, sticky=(W, N, S, E))
        # this get changed from update_current_visual_distance
        self.text_distance = Text(master, width=10, height=1, bg='lightgreen', fg="red", font=('times', 12, 'bold'))
        self.text_distance.grid(row=0, column=3, sticky=(W, N, S, E))


    def update_round_visual_element(self):
        label_round = ttk.Label(self.frame, text="Current round:", background='lightgreen',
                                font=('times', 12, 'bold'))
        label_round.grid(row=8, column=0, sticky=(W, N, S, E))
        # this get changed from update_current_visual_distance
        self.text_round = Label(self.frame, bg='lightgreen', font=('times', 12, 'bold'))
        self.text_round.grid(row=8, column=1, sticky=(W, N, S, E))

    def update_visual_round(self, round):
        """
            Each time we want to update the distance on the GUI
            we call this passing the distance as parameter
        """
        self.text_round.config(text=round)

    def create_initial_population_visual_element(self):
        var = StringVar(self.frame)
        var.set("shuffle")  # initial value
        label_distance = ttk.Label(self.frame, text="Select mode:", background='lightgreen', font=('times', 12, 'bold'))
        label_distance.grid(row=0, column=0, sticky=(W, N, S))
        option1 = OptionMenu(self.frame, var, "shuffle", "elitism")
        option1.grid(row=0, column=1, sticky=(W, N, S))
        label_population = ttk.Label(self.frame, text="Choose population size", background="lightblue",
                                     font=('times', 12, 'bold'))
        label_population.grid(row=1, column=0, columnspan=2, sticky=(E, W, N, S))
        self.w = Scale(self.frame, from_=150, to=1000, resolution=10, orient=HORIZONTAL)
        self.w.grid(row=2, column=0, columnspan=2, sticky=(E, W, N, S))
        button = Button(self.frame, text="Create initial population", pady=5,
                        command=lambda: self.create_initial_population_button(var.get()))
        button.grid(row=3, column=0, columnspan=2, sticky=(E, W, N, S))

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

            self.plot_points(self.newtsp.city_tour_tuples)
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
        tour_tuples.append(tour_tuples[0])
        data_in_array = np.array(tour_tuples)
        transposed = data_in_array.T
        x, y = transposed
        plt.ion()
        self.a.cla()
        # self.f, self.a = plt.subplots(1, 1)
        # self.f = Figure(figsize=(8, 6), dpi=100)
        # self.a = self.f.add_subplot(111, navigate=True)
        self.a.plot(x, y, 'ro')
        self.a.plot(x, y, 'b-')
        # self.a.set_title('Current best tour')
        # self.a.set_xlabel('X axis coordinates')
        # self.a.set_ylabel('Y axis coordinates')
        # self.a.grid(True)
        # self.canvas = FigureCanvasTkAgg(self.f, master=root)
        # self.canvas.mpl_connect('motion_notify_event', on_move)
        # self.canvas.get_tk_widget().grid(row=1, column=1, sticky=W)
        self.canvas.draw()
        # self.canvas.show()

    def plot_points(self, tour_tuples):
        """
            We call this passing the list of tuples with city
            coordinates to plot the tour we want on the GUI
        """
        data_in_array = np.array(tour_tuples)
        transposed = data_in_array.T
        x, y = transposed
        plt.ion()
        # self.f, self.a = plt.subplots(1, 1)
        self.f = Figure(figsize=(8, 6), dpi=100)
        self.a = self.f.add_subplot(111, navigate=True)
        self.a.plot(x, y, 'ro')
        # self.a.plot(x, y, 'b-')
        self.a.set_title('Current best tour')
        self.a.set_xlabel('X axis coordinates')
        self.a.set_ylabel('Y axis coordinates')
        self.a.grid(True)
        self.canvas = FigureCanvasTkAgg(self.f, master=root)
        self.canvas.mpl_connect('motion_notify_event', on_move)
        self.canvas.get_tk_widget().grid(row=1, column=1, sticky=W)
        self.canvas.draw()
        self.canvas.show()


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
        button1.grid(row=4, column=0, columnspan=2, sticky=(E, W, N, S))


    def create_init_pop(self, init_dict, init_tour, type):
        """
            We create the initial population with TSPInitialPopulation class
            we pass the dict with cities and coordinates and the initial tour
        """
        self.initial_population_size = self.w.get()
        new_pop = TSPInitialPopulation(init_dict, init_tour, self.initial_population_size,
                                       type)  # plus the population initial size (here is 200)
        return new_pop.pop_group

    def create_offsprings_round_one(self):
        tsp_ga_solve = TSPGeneticAlgo(self.temp, self.init_tour, self.best_tour[0])
        offspring_distances_list = []
        for offspring in tsp_ga_solve.offsprings:
            offspring.append(offspring[0])
            offspring_distance = TSPDistance(offspring, self.city_coords)
            offspring.pop()
            offspring_distances_list.append((offspring_distance.distance_cost, offspring_distance.tourlist))
        self.local_temp = sorted(offspring_distances_list, key=lambda x: x[0])
        # while len(self.local_temp) > 100:
        # self.local_temp.pop()
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
        label_rounds = ttk.Label(self.frame, text="Choose rounds", background="lightblue",
                                 font=('times', 12, 'bold'))
        label_rounds.grid(row=5, column=0, columnspan=2, sticky=(E, W, N, S))
        self.crounds = Scale(self.frame, from_=1, to=10000, resolution=100, orient=HORIZONTAL)
        self.crounds.grid(row=6, column=0, columnspan=2, sticky=(E, W, N, S))
        button2 = Button(self.frame, text="Start genetic algorithm", pady=3, command=lambda: self.start_solving())
        button2.grid(row=12, column=0, columnspan=2, sticky=(E, W, N, S))
        label_p = ttk.Label(self.frame, text="Crossover probability", background="lightblue",
                            font=('times', 12, 'bold'))
        label_p.grid(row=9, column=0, columnspan=2, sticky=(E, W, N, S))
        self.p = Scale(self.frame, from_=0.1, to=1, resolution=0.1, orient=HORIZONTAL)
        self.p.grid(row=10, column=0, columnspan=2, sticky=(E, W, N, S))
        return self

    def start_solving(self):
        def callback():
            self.round_pop_size = self.initial_population_size - 100
            rounds = self.crounds.get()
            self.update_round_visual_element()
            if self.p.get() == 0.1:
                self.p.set(0.9)
            for i in range(rounds):
                p = self.p.get()
                print p
                print i
                round = i
                circle = circleGA(self.temp, self.local_temp, self.init_tour, self.best_tour[0], self.city_coords,
                                  self.round_pop_size, p)
                children_distances_list = []
                children_distances_list[:] = []
                for child in circle.offsprings:
                    child.append(child[0])
                    child_distance = TSPDistance(child, self.city_coords)
                    child.pop()
                    children_distances_list.append((child_distance.distance_cost, child_distance.tourlist))
                self.local_temp[:] = []
                self.local_temp = sorted(children_distances_list, key=lambda x: x[0])
                self.temp[:] = []
                self.temp = circle.initial_population
                children_shortest_path = []
                children_shortest_path[:] = []
                children_shortest_path_cost = min(i[0] for i in self.local_temp)
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
                self.update_visual_round(round)

        t = threading.Thread(target=callback)
        t.start()


b = VisualSolve(root)
root.mainloop()