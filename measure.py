import math

def distance(x1, y1, x2, y2):
    result = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
    return result


def to_cm(dots, dots_per_cm):
    return round(dots / dots_per_cm , 1)

card_w_px = distance(488, 750, 552, 744)
card_h_px = distance(516, 769, 520, 727)

scale_w = card_w_px / 8.56
scale_h = card_h_px / 5.4

dots_per_cm = (scale_w + scale_h) / 2

chest_px = distance(204, 491, 603, 504)
chest_cm = to_cm(chest_px, dots_per_cm)


print(chest_cm)
print(scale_w)
print(scale_h)
print(dots_per_cm)