import matplotlib
import numpy as np
from matplotlib import figure

from events_handler.events import EventsHandler, EventTypes, SubscriberRole


class Plotter:
    @classmethod
    def __init__(cls):
        EventsHandler.subscribe(EventTypes.PLOT_REQUEST, SubscriberRole.PROVIDER, cls.on_plot_request)

    @classmethod
    def on_plot_request(cls, data):
        return cls.plot_data(data)

    @classmethod
    def plot_data(cls, data):
        fig = matplotlib.figure.Figure(figsize=(8, 5), dpi=100)
        fig.add_subplot(111).plot(*zip(*data),
                                  '--p',
                                  color='gray',
                                  markersize=4,
                                  linewidth=1,
                                  markerfacecolor='red',
                                  markeredgecolor='blue',
                                  markeredgewidth=0.5)
        return fig
