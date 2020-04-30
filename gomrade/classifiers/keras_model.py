import cv2
import keras
import tensorflow as tf
import numpy as np


class_mapping = {
    '.': 0,
    'B': 1,
    'W': 2,
}
class_mapping_inv = {v: k for k, v in class_mapping.items()}


def crop_stone(image, x, y, x_margin=16, y_margin=16):
    mask = np.zeros((x_margin*2, y_margin*2))
    mask_x_start = 0
    mask_y_start = 0
    mask_x_stop = x_margin + y_margin
    mask_y_stop = x_margin + y_margin

    x_start = x - x_margin
    x_stop = x + x_margin
    y_start = y - y_margin
    y_stop = y + y_margin
    if x-x_margin < 0:
        mask_x_start = x_margin
        mask_x_stop = x_margin*2
        x_start = 0
        x_stop = x_margin

    elif x+x_margin > image.shape[0]:
        mask_x_start = 0
        mask_x_stop = x_margin
        x_start = image.shape[0] - x_margin
        x_stop = image.shape[0]

    if y-y_margin < 0:
        mask_y_start = y_margin
        mask_y_stop = y_margin*2
        y_start = 0
        y_stop = y_margin
    elif y+y_margin > image.shape[1]:
        mask_y_start = 0
        mask_y_stop = y_margin
        y_start = image.shape[1] - y_margin
        y_stop = image.shape[1]

    mask[mask_x_start:mask_x_stop, mask_y_start:mask_y_stop] = image[x_start:x_stop, y_start:y_stop]
    return mask


class KerasModel:
    def __init__(self, path=None):
        self.model = None
        if path is not None:
            self.model = self._load_from_state(path)

    def _load_from_state(self, path):
        with tf.device('/cpu:0'):
            return keras.models.load_model(path,  custom_objects={"softmax_v2": tf.nn.softmax})

    def dump(self, exp_dir):
        raise NotImplementedError()

    def fit(self, config, cap):

        return self

    def read_board(self, image, x_grid, y_grid, debug=False):
        # frame = cv2.blur(frame, ksize=(10, 10))

        frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        stones_state = []
        for x in x_grid:
            for y in y_grid:
                cropped = crop_stone(frame, x, y, x_margin=16, y_margin=16)
                cropped = cropped.reshape(-1).reshape(1, 32, 32, 1)/256
                # cropped = cropped.reshape(1, -1)/256
                c = self.model.predict(cropped)
                c = np.argmax(c, axis=1)[0]
                c = class_mapping_inv[c]
                stones_state.append(c)

        return stones_state, image

