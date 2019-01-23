import math
from scipy.spatial.distance import euclidean

# red
points1 =[((-694, -719), (694, 719)), ((-691, -722), (698, 715)), ((-723, 690), (739, -673)), ((-699, 714), (714, -699))]

# white
points2 = [((-706, -707), (707, 706)), ((-723, 690), (739, -673)), ((-731, 681), (754, -656)), ((-660, 751), (678, -735)), ((-699, 714), (714, -699)), ((-709, -704), (704, 709)), ((-694, 719), (719, -694))]



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


dists = []
diff = {}
for p1 in points1:
    for p2 in points2:
        if p1 == p2:
            continue
        line1 = calc_line(p1)
        line2 = calc_line(p2)
        if abs(line1[0] - line2[0]) < 0.1:
            dist = calc_dist((line1, line2))
            dists.append(dist)
            diff[dist] = line1[2] - line2[2]
        # print(calc_line(p1))
        # print(calc_line(p2))
        # dists.append(dist1)

print(dists)
print(min(dists))
print(diff[min(dists)])
if diff[min(dists)] < 0:
    print('↓')
else:
    print('↑')
# >0 downwards
# <0 upwards