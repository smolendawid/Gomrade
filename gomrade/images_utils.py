import numpy as np


def get_pt_color(frame, pts, num_neighbours):
    colors = []
    for pt in pts:
        i = pt[0]
        j = pt[1]
        start_i = i - num_neighbours
        stop_i = i + num_neighbours
        start_j = j - num_neighbours
        stop_j = j + num_neighbours
        area = frame[start_j: stop_j, start_i: stop_i, :]
        mean_rgb = np.mean(np.mean(area, axis=0), axis=0)
        colors.append(mean_rgb)

    return colors


def fill_buffer(cap, buffer_size):
    buffer = []
    for _ in range(buffer_size):
        _, frame = cap.read()
        buffer.append(frame)
    return buffer


def avg_images(images):  # average an array of images to remove some video noise
    output = np.zeros(images[0].shape, dtype="float32")
    for i in images:
        output += i
    output /= len(images)
    return output.astype("uint8")

