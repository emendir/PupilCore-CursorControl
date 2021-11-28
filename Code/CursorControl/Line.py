"""This module contains some coordinate geometry functions."""
from math import sqrt


class Line():
    def __init__(self, point1, point2):
        a = point1[0]
        b = point1[1]
        c = point2[0]
        d = point2[1]

        #print(a, b, c, d)
        self.v = (d-b)/(c-a)
        self.e = b-self.v*a
        pass


def PointFurtherOn(point, slope, distance):
    """Calculates the the coordinates of a point a certain distance
    and a certain angle <slope> away from a first coordinate point"""
    return Line(point, (point[0] + 1, point[1]+slope))


def Intersection(line1, line2):
    """Calculates the coordinates of the intersection point between two lines"""
    v1 = line1.v
    v2 = line2.v
    e1 = line1.e
    e2 = line2.e

    x = (e2-e1)/(v1-v2)
    y = v1*x+e1

    return(x, y)


def DistanceTwixPoints(point1, point2):
    """Calculates the distance between two coordinate points"""
    x = point2[0]-point1[0]
    y = point2[1]-point1[1]
    return sqrt(x**2+y**2)
