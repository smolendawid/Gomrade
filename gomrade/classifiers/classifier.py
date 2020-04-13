import numpy as np


def get_mean_color(a):
    return np.median(np.median(a, axis=0), axis=0)


def classify_brightness(rgb_tuple, dominant_color):

    brightness = sum(rgb_tuple)
    if brightness < 80:
        color = "k"
    elif brightness > 600:
        color = "w"
    else:
        color = "v"

    return color


def closest_color(rgb_tuple, board_colors, black_colors, white_colors) -> str:
    """Manhattan distance, colors should be in tuple (r,g,b)
    return the closest color: `W` `B` or `.`"""
    colors = []

    for color in board_colors:
        colors.append(('.', color))

    for color in white_colors:
        colors.append(('W', color))

    for color in black_colors:
        colors.append(('B', color))

    manhattan = lambda x,y : abs(x[0] - y[0]) + abs(x[1] - y[1]) + abs(x[2] - y[2])
    # manhattan = lambda x,y : abs(x[2] - y[2])
    distances = {k: manhattan(v, rgb_tuple) for k, v in colors}
    color = min(distances, key=distances.get)

    return color
