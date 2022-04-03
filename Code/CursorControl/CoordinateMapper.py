from math import sqrt


def MapCoordinates(coordinates, corners, resolution):
    """
    coordinates [x,y]: Coordinates on the original coordinate system of the point to map.
    corners [[x,y],[x,y],[x,y],[x,y]]: Coordinates of the four corners of the bounding box around the distorted coordinate system  onto which to map
                                        bottom left, bottom right, top left, top right
    resolution [r_x, r_y]: the width and height of the bounding box of the distorted coordinate system in its own coordinate system
    """
    h, l = coordinates
    a, b, c, d = corners
    # Calculating part 1 of the formula for coordinate mapping
    sqrt_arg = ((pow(h, 2) - 2 * a[0] * h + pow(a[0], 2)) * pow(d[1], 2) + (((-2 * pow(h, 2)) + (2 * b[0] + 2 * a[0]) * h - 2 * a[0] * b[0]) * c[1] + ((-2 * pow(h, 2)) + (2 * c[0] + 2 * a[0]) * h - 2 * a[0] * c[0]) * b[1] +
                                                                            (2 * pow(h, 2) + (2 * d[0] - 4 * c[0] - 4 * b[0] + 2 * a[0]) * h - 2 * a[0] * d[0] + 4 * b[0] * c[0]) * a[1] + (((-2 * d[0]) + 2 * c[0] + 2 * b[0] - 2 * a[0]) * h +
                                                                                                                                                                                            2 * a[0] * d[0] + (2 * a[0] - 4 * b[0]) * c[0] + 2 * a[0] * b[0] - 2 * pow(a[0], 2)) * l) * d[1] +
                (pow(h, 2) - 2 * b[0] * h + pow(b[0], 2)) * pow(c[1], 2) + ((2 * pow(h, 2) + ((-1 * 4 * d[0]) + 2 * c[0] + 2 * b[0] - 4 * a[0]) * h + 4 * a[0] * d[0] - 2 * b[0] * c[0]) * b[1] + ((-2 * pow(h, 2)) + (2 * d[0] + 2 * b[0]) * h - 2 * b[0] * d[0]) * a[1] +
                                                                            ((2 * d[0] - 2 * c[0] - 2 * b[0] + 2 * a[0]) * h + (2 * b[0] - 4 * a[0]) * d[0] + 2 * b[0] * c[0] - 2 * pow(b[0], 2) +
                                                                             2 * a[0] * b[0]) * l) * c[1] + (pow(h, 2) - 2 * c[0] * h + pow(c[0], 2)) * pow(b[1], 2) +
                (((-2 * pow(h, 2)) + (2 * d[0] + 2 * c[0]) * h - 2 * c[0] * d[0]) * a[1] +
                 ((2 * d[0] - 2 * c[0] - 2 * b[0] + 2 * a[0]) * h + (2 * c[0] - 4 * a[0]) * d[0] - 2 * pow(c[0], 2) + (2 * b[0] + 2 * a[0]) * c[0]) * l) * b[1] +
                (pow(h, 2) - 2 * d[0] * h + pow(d[0], 2)) * pow(a[1], 2) + (((-2 * d[0]) + 2 * c[0] + 2 * b[0] - 2 * a[0]) * h - 2 * pow(d[0], 2) + (2 * c[0] + 2 * b[0] + 2 * a[0]) * d[0] - 4 * b[0] * c[0]) * l * a[1] +
                (pow(d[0], 2) + ((-2 * c[0]) - 2 * b[0] + 2 * a[0]) * d[0] + pow(c[0], 2) + (2 * b[0] - 2 * a[0]) * c[0] + pow(b[0], 2) - 2 * a[0] * b[0] + pow(a[0], 2)) * pow(l, 2))
    if sqrt_arg < 0:    # checking that this part of the equation won't throw a maths error
        return
    # calculating part 2 of the formula if part 1 went well
    p = (sqrt(sqrt_arg) +
         (h - a[0]) * d[1] + ((-1 * h) - b[0] + 2 * a[0]) * c[1] + (c[0] - h) * b[1] + (h + d[0] - 2 * c[0]) * a[1] + ((-1 * d[0]) + c[0] + b[0] - a[0]) * l) / (
        (2 * b[0] - 2 * a[0]) * d[1] + (2 * a[0] - 2 * b[0]) * c[1] + (2 * c[0] - 2 * d[0]) * b[1] + (2 * d[0] - 2 * c[0]) * a[1])

    q = (l - (a[1] + p * (b[1] - a[1]))) / \
        ((c[1] + p * (d[1] - c[1])) - (a[1] + p * (b[1] - a[1])))
    # print("q:", q)
    return (p * resolution[0], q * resolution[1])
