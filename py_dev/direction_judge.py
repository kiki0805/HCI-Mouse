import math
from scipy.spatial.distance import euclidean


def move_direction(red_points, white_points):
    points1 = red_points
    points2 = white_points
    dists = []
    diff = {}
    for p1 in points1:
        for p2 in points2:
            # print(p1[0][0] - p1[1][0], p2[0][0] - p2[1][0])
            if p1[0][0] == p1[1][0] and p2[0][0] == p2[1][0]:
                if p1[0][0] - p2[0][0] > 0:
                    return 180
                else:
                    return 0
            if p1 == p2 or p1[0][0] == p1[1][0] or p2[0][0] == p2[1][0]:
                continue
            line1 = calc_line(p1)
            line2 = calc_line(p2)
            # print('dist of k ' + str(abs(line1[0] - line2[0])))
            if abs(line1[0] - line2[0]) < 0.1:
                dist = calc_dist((line1, line2))
                dists.append(dist)
                diff[dist] = line1[2] - line2[2]

    if dists == []:
        return 'None'
    if diff[min(dists)] < 0:
        # print('↓')
        return '↓'
    else:
        # print('↑')
        return '↑'


def calc_line(points):
    x1, y1 = points[0]
    x2, y2 = points[1]
    # kx - y + b = 0
    # A = k, B = -1, C = b
    k = (y2-y1) / (x2-x1)
    b = y1 - k * x1
    return k, -1, b


def calc_dist(lines):
    a1, b1, c1 = lines[0]
    a2, b2, c2 = lines[1]
    a = (a1 + a2) / 2
    b = (b1 + b2) / 2
    # |c1-c2| / (A^2+B^2)
    return abs(c1 - c2) / (a*a + b*b)



