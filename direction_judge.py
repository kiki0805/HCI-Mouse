import math
from scipy.spatial.distance import euclidean


def move_direction(data):
    points1, points2, red_rhos, white_rhos, red_thetas, white_thetas = data
    dists = []
    diff = {}
    for i in range(len(points1)):
        for j in range(len(points2)):
            p1 = points1[i]
            p2 = points2[j]
            # if (p1[0][0] == p1[1][0] and abs(p2[0][0] - p2[1][0]) < 105) or \
            #         (p2[0][0] == p2[1][0] and abs(p1[0][0] - p1[1][0]) < 105):
            if p1[0][0] == p1[1][0] and p2[0][0] == p2[1][0]:
                if (p1[0][0] + p1[1][0]) - (p2[0][0] + p2[1][0]) < 0:
                    return 0
                else:
                    return 180
            # if p1 == p2 or p1[0][0] == p1[1][0] or p2[0][0] == p2[1][0]:
            if p1 == p2:
                continue
            if p1[0][0] == p1[1][0] or p2[0][0] == p2[1][0]:
                if p1[0][0] + p1[1][0] < p2[0][0] + p2[1][0]:
                    return '↓'
                elif p1[0][0] + p1[1][0] > p2[0][0] + p2[1][0]:
                    return '↑'
                return 'None'

            red_rho = red_rhos[i]
            white_rho = white_rhos[j]
            red_theta = red_thetas[i]
            white_theta = white_thetas[j]

            line1 = calc_line(p1)
            line2 = calc_line(p2)

            # print('diff of rho: ',end='')
            # print(red_rho - white_rho)
            # print('diff of theta: ', end='')
            # print(red_theta - white_theta)
            # if abs( - white_rho) < 1.1 and abs(red_theta - white_theta) < 0.3:
            #     dist = calc_dist((line1, line2))
            #     dists.append(dist)
            #     diff[dist] = line1[2] - line2[2]
            #     print('diff of rho: ',end='')
            #     print(red_rho - white_rho)
            #     print(red_theta, white_theta)
            #     print('diff of theta: ', end='')
            #     print(red_theta - white_theta)
            #     if abs(red_theta - white_theta) < 0.3:
            #         if red_theta > 0:
            #             if red_rho - white_rho > 0:
            #                 return '↓'
            #             return '↑'
            #         if red_rho - white_rho > 0:
            #             return '↑'
            #         return '↓'
            # if abs( - white_rho) < 1.1 and abs(red_theta - white_theta) < 0.3:
            if red_theta - white_theta == 0 and abs( - white_rho) < 0.4:
                if red_theta > 0 and red_rho - white_rho < 0:
                    return '↓'
                elif red_theta > 0 and red_rho - white_rho > 0:
                    return '↑'
                elif red_theta < 0 and red_rho - white_rho > 0:
                    return '↓'
                elif red_theta < 0 and red_rho - white_rho < 0:
                    return '↑'
            if red_rho - white_rho == 0 and abs(red_theta - white_theta) < 0.3:
                if red_theta > 0 and red_theta - white_theta < 0:
                    return '↓'
                elif red_theta > 0 and red_theta - white_theta > 0:
                    return '↑'
                elif red_theta < 0 and red_theta - white_theta < 0:
                    return '↑'
                elif red_theta < 0 and red_theta - white_theta > 0:
                    return '↓'
            # if abs( - white_rho) < 0.4 and abs(red_theta - white_theta) < 0.3:
            #     if red_theta - white_theta < 0 and red_rho - white_rho < 0:
            #         return '↓'
            #     elif red_theta - white_theta > 0 and red_rho - white_rho > 0:
            #         return '↑'


            # # print('Direction judge: ', end='')
            # # print(p1, p2)
            # # print('Line args: ', end='')
            # # print(line1, line2)
            # print('dist of k ' + str(abs(line1[0] - line2[0])))

            if abs(line1[0] - line2[0]) < 0.4 or (abs(red_rho - white_rho) < 0.4 and abs(red_theta - white_theta) < 0.3):
                dist = calc_dist((line1, line2))
                dists.append(dist)
                diff[dist] = line1[2] - line2[2]
            # # print(abs(line1[0] - line2[0]))

    if dists == [] or abs(diff[min(dists)]) > 3:
        return 'None'
    # count = 0
    # for i in dists:
    #     if diff[i] < 0:
    #         count += 1
    # if count * 2 > len(dists):
    #     return '↓'
    # else:
    #     return '↑'
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



