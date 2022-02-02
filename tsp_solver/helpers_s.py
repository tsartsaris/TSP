import math


def euclidean_distance(p0, p1):
    """
        Calculates the Euclidean distance between 2 points (x1,y1) and (x2,y2)
    """
    print(p0, p1)
    xdiff = float(p1[0]) - float(p0[0])
    ydiff = float(p1[1]) - float(p0[1])
    return int(math.sqrt((xdiff * xdiff + ydiff * ydiff) + 0.5))


def calculate_distance(route):
    """
        Iterates a a_list of coordinate tuples and calculates the Euclidean
        distance between 2 points found sequential in the a_list representing
        the tour. Then sums everything up and returns the result
    """
    inner_sum =  sum([euclidean_distance(v, w) for v, w in zip(route, route[1:])])
    outer_sum = euclidean_distance(route[-1], route[1])
    total = inner_sum + outer_sum
    return total
