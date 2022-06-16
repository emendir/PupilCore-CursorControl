"""This module contains some coordinate geometry functions."""
from math import sqrt, sin, cos


class Line():
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2
        self.a = point1[0]
        self.b = point1[1]
        self.c = point2[0]
        self.d = point2[1]

        #print(a, b, c, d)
        self.slope = (self.d-self.b)/(self.c-self.a)  # slope
        self.e = self.b-self.slope*self.a

        pass

    def length(self):
        return DistanceTwixPoints((self.a, self.b), (self.c, self.d))


def PointFurtherOn(point, slope, distance):
    """Calculates the the coordinates of a point a certain distance
    and a certain angle <slope> away from a first coordinate point"""

    a = sqrt(pow(distance, 2)/(1+pow(slope, 2)))
    b = slope*a
    # return (point[0] + 1, point[1]+slope)
    return (point[0] + a, point[1] + b)


def Intersection(line1, line2):
    """Calculates the coordinates of the intersection point between two lines"""
    v1 = line1.slope
    v2 = line2.slope
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
