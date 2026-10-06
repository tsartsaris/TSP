# -*- coding: utf-8 -*-
"""
Distances between cities, following the TSPLIB rules.

TSPLIB is the standard library of Travelling Salesman benchmark problems. Every
problem file declares an EDGE_WEIGHT_TYPE that says how the distance between two
cities is measured. Using exactly the same rule as TSPLIB matters: it is the only
way the tour lengths we compute can be compared with the published optimal values.

Two types are supported:

    EUC_2D  cities are points on a plane, distance is the straight line between them
    GEO     cities are (latitude, longitude) on the Earth, distance is in kilometres

Both functions return whole numbers, because TSPLIB rounds every single edge
before adding the edges of a tour together.
"""

__author__ = "Tsartsaris Sotiris"
__copyright__ = "Copyright 2014, The TSP Project"
__license__ = "APACHE 2.0"

import math

EARTH_RADIUS_KM = 6378.388  # the radius TSPLIB uses for GEO problems
TSPLIB_PI = 3.141592        # TSPLIB uses this truncated value of pi; math.pi would change the results


def euclidean_distance(p0, p1):
    """
        Straight-line distance between two points (x, y), rounded to the nearest
        integer ("nint" in the TSPLIB documentation).

        >>> euclidean_distance((0, 0), (3, 4))
        5
    """
    return int(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) + 0.5)


def _geo_to_radians(coordinate):
    """
        TSPLIB writes GEO coordinates as DDD.MM, i.e. degrees and *minutes*, not
        decimal degrees: 16.47 means 16 degrees and 47 minutes. Minutes are
        sixtieths of a degree, so the fractional part is scaled by 100/60 = 5/3
        before converting degrees to radians.
    """
    degrees = int(coordinate)
    minutes = coordinate - degrees
    return TSPLIB_PI * (degrees + 5.0 * minutes / 3.0) / 180.0


def geo_distance(p0, p1):
    """
        Distance in km between two points given as (latitude, longitude) in
        TSPLIB's DDD.MM format, measured along the surface of the Earth.

        This is the spherical law of cosines written the way TSPLIB writes it.
        TSPLIB truncates the result after adding 1 instead of rounding.

        >>> geo_distance((0.0, 0.0), (0.0, 1.0))  # one degree along the equator
        112
    """
    lat0, lon0 = _geo_to_radians(p0[0]), _geo_to_radians(p0[1])
    lat1, lon1 = _geo_to_radians(p1[0]), _geo_to_radians(p1[1])
    q1 = math.cos(lon0 - lon1)
    q2 = math.cos(lat0 - lat1)
    q3 = math.cos(lat0 + lat1)
    cosine = 0.5 * ((1.0 + q1) * q2 - (1.0 - q1) * q3)
    # floating point can push the cosine of two identical points just above 1,
    # which is outside the domain of acos, so clamp it
    return int(EARTH_RADIUS_KM * math.acos(min(1.0, cosine)) + 1.0)


# The EDGE_WEIGHT_TYPE written in a .tsp file -> the function that measures it
DISTANCE_FUNCTIONS = {
    "EUC_2D": euclidean_distance,
    "GEO": geo_distance,
}
