import cv2
import keras
import tensorflow as tf
import numpy as np
from utils.rewrite_images_to_df import crop_stone, class_mapping

class_mapping_inv = {v: k for k, v in class_mapping.items()}


class KerasModel:
    def __init__(self, path=None):
        self.model = None
        if path is not None:
            self.model = self._load_from_state(path)

    def _load_from_state(self, path):
        with tf.device('/cpu:0'):
            return keras.models.load_model(path,  custom_objects = {"softmax_v2": tf.nn.softmax})

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

