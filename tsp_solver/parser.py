import re
from typing import List, Dict

from events_handler.events import EventsHandler, EventTypes, SubscriberRole


def check_filename_tsp(filename):
    """
        Check if the file provided is a valid TSP file
        ...ends with .tsp
    """
    if filename.endswith(".tsp"):
        return True
    else:
        return False


def read_tsp_file_contents(filename):
    with open(filename) as f:
        content = f.read().splitlines()
        print(content)
        return content


class TSPParser:
    filename: str = None
    subscribed: bool = False
    dimension: int = None
    tsp_file_contents: List = []
    tsp_cities: Dict = {}

    @classmethod
    def __init__(cls):
        print("TSP PARSER INITIATED")
        EventsHandler.subscribe(EventTypes.TSP_FILE_OPENED, SubscriberRole.LISTENER, cls.on_file_selected)
        EventsHandler.subscribe(EventTypes.TSP_DATA_REQUEST, SubscriberRole.SUNSCRIBER, cls.on_data_requested)

    @classmethod
    def on_file_selected(cls, data):
        cls.clear_data()
        cls.filename = data
        cls.open_tsp_file()

    @classmethod
    def on_data_requested(cls, data):
        if data is List:
            return cls.tsp_cities.values()
        if data is Dict:
            return cls.tsp_cities

    @classmethod
    def open_tsp_file(cls):
        if not check_filename_tsp(cls.filename):
            # TODO raise a custom exception
            print("File is not TSP file")
        else:
            cls.tsp_file_contents = read_tsp_file_contents(cls.filename)
            cls.detect_dimension()

    @classmethod
    def detect_dimension(cls):
        for record in cls.tsp_file_contents:
            if record.startswith("DIMENSION"):
                parts = record.split(":")
                cls.dimension = int(parts[1])
                print(cls.dimension)
        cls.get_cities_dict()

    @classmethod
    def get_cities_dict(cls):
        zero_index = cls.tsp_file_contents.index("NODE_COORD_SECTION") + 1
        for index in range(zero_index, zero_index + cls.dimension):
            parts = cls.tsp_file_contents[index].strip()
            city_coords_parts = re.findall(r"[+-]?\d+(?:\.\d+)?", parts)
            cls.tsp_cities[city_coords_parts[0]] = (float(city_coords_parts[1]), float(city_coords_parts[2]))
        EventsHandler.post_event(event_type=EventTypes.PLOT_REQUEST, data=cls.tsp_cities.values())

    @classmethod
    def clear_data(cls):
        cls.filename = ""
        cls.tsp_cities = {}
        cls.tsp_file_contents = []
        cls.dimension = 0

