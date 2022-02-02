# from tkinter import Tk
#
# window = Tk()
#
#
# # add widgets here
#
# def create_main_window():
#     window.title('TSP Solver')
#     window.geometry("1027x768")
#     return window
#
#
# create_main_window()

# !/usr/bin/env python
import os
import sys

from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib
from matplotlib import figure

matplotlib.use('TkAgg')

"""
Demonstrates one way of embedding Matplotlib figures into a PySimpleGUI window.
Basic steps are:
 * Create a Canvas Element
 * Layout form
 * Display form (NON BLOCKING)
 * Draw plots onto convas
 * Display form (BLOCKING)

 Based on information from: https://matplotlib.org/3.1.0/gallery/user_interfaces/embedding_in_tk_sgskip.html
 (Thank you Em-Bo & dirck)
"""

# ------------------------------- PASTE YOUR MATPLOTLIB CODE HERE -------------------------------
#
# # Goal is to have your plot contained in the variable  "fig"
#
# # Fixing random state for reproducibility
# np.random.seed(19680801)
#
# # make up some fig in the interval ]0, 1[
# y = np.random.normal(loc=0.5, scale=0.4, size=1000)
# y = y[(y > 0) & (y < 1)]
# y.sort()
# x = np.arange(len(y))
#
# # plot with various axes scales
# plt._figure(1)
#
# # linear
# plt.subplot(221)
# plt.plot(x, y)
# plt.yscale('linear')
# plt.title('linear')
# plt.grid(True)
#
# # log
# plt.subplot(222)
# plt.plot(x, y)
# plt.yscale('log')
# plt.title('log')
# plt.grid(True)
#
# # symmetric log
# plt.subplot(223)
# plt.plot(x, y - y.mean())
# plt.yscale('symlog', linthreshy=0.01)
# plt.title('symlog')
# plt.grid(True)
#
# # logit
# plt.subplot(224)
# plt.plot(x, y)
# plt.yscale('logit')
# plt.title('logit')
# plt.grid(True)
# plt.gca().yaxis.set_minor_formatter(NullFormatter())
# plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
#                     wspace=0.35)
# fig = plt.gcf()
#


fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=100)
t = np.arange(0, 3, .01)
fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))


# ------------------------------- END OF YOUR MATPLOTLIB CODE -------------------------------

# ------------------------------- Beginning of Matplotlib helper code -----------------------

def draw_figure(canvas, _figure):
    figure_canvas_agg = FigureCanvasTkAgg(_figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


# ------------------------------- Beginning of GUI CODE -------------------------------

# define the window plot_column
plot_column = [[sg.Text('Plot test')],
               [sg.Canvas(key='-CANVAS-')],
               [sg.Button('Ok')]]

input_column = [
    [sg.Text('Select file', size=12)],
    [sg.Listbox(values=[], enable_events=True, size=(25, 10), key="-FILE LIST-", font=('Arial', 9))],
    [sg.Button('Solve', key="-SOLVE-")]]

from os import listdir
from os.path import isfile, join

onlyfiles = [os.path.join("./TSP_Problems", f) for f in listdir("./TSP_Problems") if
             isfile(join("./TSP_Problems", f)) and f.endswith(".tsp")]
print(onlyfiles)

layout = [[sg.Column(plot_column), sg.VSeparator(), sg.Column(input_column)]]

# create the form and show it without the plot


# add the plot to the window
# fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)


# window.close()
# sys.exit()

from events_handler.events import EventsHandler, EventTypes, SubscriberRole


class MainWindow:
    def __init__(self):
        self.window = None
        self.figure_canvas_agg = None
        self.create_main_window()
        self.update_window_file_list()
        EventsHandler.subscribe(EventTypes.PLOT_REQUEST, SubscriberRole.CONSUMER,  self.show_plot)
        EventsHandler.post_event(event_type=EventTypes.PLOT_REQUEST, data=[(1, 1)])

    def create_main_window(self):
        self.window = sg.Window('Demo Application - Embedding Matplotlib In PySimpleGUI', layout, finalize=True,
                                element_justification='center', font='Helvetica 18',relative_location=(-200, -200))

    def update_window_file_list(self):
        self.window["-FILE LIST-"].update(onlyfiles)

    def run(self):
        while True:
            event, values = self.window.read()
            if event == "Ok" or event == sg.WIN_CLOSED:
                break
            elif event == "-FILE LIST-":
                EventsHandler.post_event(EventTypes.TSP_FILE_OPENED, values["-FILE LIST-"][0])
            elif event == "-SOLVE-":
                EventsHandler.post_event(EventTypes.SOLVE, None)

    def show_plot(self, data):
        if self.figure_canvas_agg is not None:
            self.figure_canvas_agg.get_tk_widget().forget()
            plt.close('all')
        plot_figure = data
        self.figure_canvas_agg = FigureCanvasTkAgg(plot_figure, self.window['-CANVAS-'].TKCanvas)
        self.figure_canvas_agg.draw()
        self.figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

