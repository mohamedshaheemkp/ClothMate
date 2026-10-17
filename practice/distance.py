from math import dist
import math

x1 = 10
y1 = 20
x2 = 40
y2 = 60

gap_x = x2 - x1
gap_y = y2 - y1

dist = math.sqrt(gap_x * gap_x + gap_y * gap_y)

print(dist)