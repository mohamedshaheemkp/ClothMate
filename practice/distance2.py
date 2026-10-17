import math

def distance(x1, y1, x2, y2):
    result = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
    return result

print(distance(10, 20, 40, 60))
print(distance(0, 0, 3, 4))
print(distance(10,20,33,55))