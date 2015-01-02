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

"""
    With this parser we check for a file if is TSP file
    and the we input the data for later usage. As an add
    we plot the current instance of tour to have a visual
    output of the data we have.
"""


class TSPParser:
    def __init__(self, filename):
        self.city_coords = {}
        self.city_tour_init = []
        self.city_tour_tuples = []
        self.filename = filename
        self.display_status = ''
        if self.check_filename(filename):
            content = self.read_filename(filename)
            self.dimension = self.get_dimension(content)
            if self.check_dimension(self.filename, self.dimension):
                self.edge_weight_type = self.get_edge_weight_type(self.content)
                self.city_coords = self.get_city_coord(self.content)
                self.city_tour_init = self.create_initial_tour()
                self.city_tour_tuples = self.create_initial_coord_tuples()

            else:
                self.display_status = ('Dimension of the file do not match with the name of the file!\n'
                                       'Please make sure you have a valid TSP data file.\n'
                                       'Please use another file or correct the one you have')
        else:
            self.display_status = 'This is not a valid TSP file, should look like example.tsp.Please use another one!'

    def check_filename(self, filename):
        """
            Check if the file provided is a valid TSP data file
            ...ends with .tsp
        """
        if self.filename.endswith(".tsp"):
            return True
        else:
            return False


    def read_filename(self, filename):
        """
            Read the TSP file line by line in a list
        """
        with open(self.filename) as f:
            self.content = f.read().splitlines()
        return self.content

    def get_dimension(self, content):
        """
            Check for the line DIMENSION and return the number
        """

        for line in self.content:
            if line.startswith("DIMENSION"):
                index, space, rest = line.partition(':')
                return rest.strip()

    def check_dimension(self, filename, dimension):
        """
            Checks if the dimension found in the TSP data matches
            the name of the file provided. ex. if you provide a file
            named "eil101.tsp" the dimension in the file should be "101"
        """
        self.dimension = dimension
        self.filename = filename
        if self.dimension in self.filename:
            return True
        else:
            return False

    def get_edge_weight_type(self, content):
        """
            Check for TSP type and return it (GEO, EUC_2D)
        """
        for line in self.content:
            if line.startswith("EDGE_WEIGHT_TYPE"):
                index, space, rest = line.partition(':')
                return rest.strip()

    def get_city_coord(self, content):
        """
            Returns the cities with their coordinates in a dict
            like {'24': ('11020', '13688'), '25': ('8468', '11136'),...
        """
        start = self.content.index("NODE_COORD_SECTION")
        end = self.content.index("EOF")
        for line in self.content[start + 1:end]:
            line = line.strip()
            city, space, coord = line.partition(" ")
            coord = coord.strip()
            x, space, y = coord.partition(" ")
            self.city_coords[int(city)] = (x.strip(), y.strip())
        return self.city_coords

    def create_initial_tour(self):
        for i in range(1, int(self.dimension) + 1):
            self.city_tour_init.append(i)
        return self.city_tour_init

    def create_initial_coord_tuples(self):
        city_tour_init = self.city_tour_init
        content = self.city_coords
        for i in city_tour_init:
            self.city_tour_tuples.append(content.get(i))
        return self.city_tour_tuples


if __name__ == '__main__':
    newtsp = TSPParser("TSP_Problems/a280.tsp")