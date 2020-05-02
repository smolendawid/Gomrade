import re

import numpy as np
import cv2
import time
import os


class VideoCaptureFolderMock:
    """
    Return images from images_root, each image will be returned for a `time_for_one_img` time.
    """
    def __init__(self, images_root, time_for_one_img=5):
        """

        :param images_root: root path with .jpg images
        :param time_for_one_img: int
        """
        self.timer_start = None
        self.images_paths = [os.path.join(images_root, path)
                             for path in os.listdir(images_root) if path.endswith('.jpg')]
        self.images_paths.sort(key=lambda f: int(re.sub('\D', '', f)))

        self.time_for_one_img = time_for_one_img
        self.image_iter = 0
        self.curr_img = None
        self.images_freqs = [0] * len(self.images_paths)

    def _reset_timer(self):
        self.timer_start = time.time()

    def release(self):
        pass

    def report(self):
        for path, freq in zip(self.images_paths, self.images_freqs):
            print(f'{path}: {freq}')

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.images_paths)

    def read(self):
        # First image
        if self.timer_start is None:
            self.curr_img = cv2.imread(self.images_paths[self.image_iter])
            self._reset_timer()

        time_from_start = time.time() - self.timer_start
        if time_from_start > 5:
            if self.image_iter < len(self.images_paths) - 1:
                self.image_iter += 1
            self.curr_img = cv2.imread(self.images_paths[self.image_iter])
            self._reset_timer()

        self.images_freqs[self.image_iter] += 1
        return None, self.curr_img


class VideoCaptureFrameMock:
    def __init__(self, frame):
        self.frame = frame

    def read(self):
        return None, self.frame

    def release(self):
        pass


def get_pt_color(frame: np.ndarray, pts: [()], num_neighbours: int) -> list:
    """ Gets mean color of pixel in `frame` in every `pts` point
    and its square neighbourhood of size `num_neighbours`"""
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


def avg_images_in_buffer(images):
    """ Average an array of images to remove some video noise"""
    output = np.zeros(images[0].shape, dtype="float32")
    for i in images:
        output += i
    output /= len(images)
    return output.astype("uint8")
