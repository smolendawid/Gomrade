import subprocess
import time

import numpy as np
import cv2
import os
import warnings

from utils.images_utils import avg_images, fill_buffer


class DataCollector:
    def __init__(self, exp_dir):
        self.exp_dir = exp_dir

    def collect(self, frame, board_state):
        pass


class Move:
    def __init__(self, first_move):
        self.c = first_move

    def switch(self):
        if self.c == 'black':
            self.c = 'white'
        else:
            self.c = 'black'

    @property
    def get(self):
        return self.c


def play_wave(m):
    """ Move value. Can be GO board coordinates, 'resign', or 'pass'"""
    # todo afplay is of MAC
    # todo mp3 is hard to play in python
    try:
        subprocess.call(["afplay", f'data/synthetized_moves/{m}.mp3'])
    except ResourceWarning:
        warnings.warn("Unable to play sound {}.mp3".format(m))


class GameTracker:
    def __init__(self, tmp_path):
        self.tmp_path = tmp_path

    def replay_position(self):
        pass
        # with open(self.tmp_path, 'w') as f:
        #     f.write()


class BoardStateInterpreter:
    def __init__(self, config, first_move):
        self.num_of_the_same = 0
        self.num_of_the_diff = 0
        self.artifact = 0
        self.trigger = False
        self.prev_stones_state = np.zeros((config['board_size'] * config['board_size'],))
        self.move = Move(first_move=first_move)

        self.artifact_limit = config['artifact_limit']
        self.move_limit = config['move_limit']
        self.accept_limit = config['accept_limit']

        self.game_tracker = GameTracker(tmp_path='data/tmp.txt')

    def interpret(self, stones_state):

        is_move = False
        if len(stones_state) == sum([1 for i, j in zip(stones_state, self.prev_stones_state) if i == j]):
            self.num_of_the_same += 1
            self.artifact = 0
            self.num_of_the_diff = 0
        else:
            if self.artifact < self.artifact_limit:
                # print("Artifact")
                self.artifact += 1
                self.num_of_the_same += 1
            else:
                self.prev_stones_state = stones_state
                self.artifact = 0
                self.num_of_the_same = 0
                self.trigger = True
            self.num_of_the_diff += 1

        # print(num_of_the_same)
        if self.move.c == 'white':
            tmp_limit = self.move_limit
        elif self.move.c == 'black':
            tmp_limit = self.accept_limit

        if self.num_of_the_same > tmp_limit:
            if self.trigger:

                self.num_of_the_same = 0
                self.trigger = False
                print("MOVE MADE")
                is_move = True

        return is_move

    def realize_move(self, engine):
        self.move.switch()
        if self.move.c == 'black':
            print('Asking for a move')
            engine.clear_board()
            self.game_tracker.replay_position()
            # engine.loadsgf(path='data/tmp.txt')
            engine.showboard()
            # m = engine.play()
            play_wave('A1')

        if self.move.c == 'white':
            play_wave('move')
            # engine.clear_board()
            # engine.loadsgf(path='data/tmp.txt')
            engine.showboard()
            print('Doing nothing')


class Visualizer:
    def __init__(self):
        pass

    def show_cam(self, frame):
        res = cv2.flip(frame, -1)
        cv2.imshow('frame', res)

    def plot_board(self, frame):
        raise NotImplementedError


class GomradeGame:
    def __init__(self, config, engine, board_extractor, board_classifier, visualizer):
        """
        The main class of the project. It uses objects to analyse crop board, classify it, and, considering defined
        logic, communicate with GTP engine.

        :param config:
        :param engine:
        :param board_extractor:
        :param board_classifier:
        :param visualizer:
        """

        self.buffer_size = config['buffer_size']
        self.board_size = config['board_size']
        self.ai_color = config['ai_color']
        self.engine = engine
        self.visualizer = visualizer
        self.board_extractor = board_extractor
        self.board_classifier = board_classifier
        self.interpreter = BoardStateInterpreter(config=config, first_move=config['ai_color'])

        self.image_ind = 0

    def _pretty_state(self, stones_state, exp_dir):

        with open(os.path.join(exp_dir, f"{self.image_ind}.txt"), 'w') as f:
            for x in range(self.board_size):
                if x != 0:
                    f.write('\n')
                for y in range(self.board_size):
                    f.write(str(stones_state[x * self.board_size + y]))
                    if y != self.board_size - 1:
                        f.write(' ')

    def _dump_image(self, frame, stones_state, exp_dir):
        cv2.imwrite(os.path.join(exp_dir, f"{self.image_ind}.png"), frame)
        self._pretty_state(stones_state, exp_dir)

    def run(self, cap, exp_dir, verbose=False):

        buf_i = 0

        # fill buffer
        buf = fill_buffer(cap, self.buffer_size)

        while True:
            start = time.time()
            # Capture frame-by-frame
            ret, frame = cap.read()

            # Average images for homogeneous colors
            buf[buf_i] = frame
            buf_i = (buf_i + 1) % self.buffer_size
            frame = avg_images(buf)

            # Crop image to board and perform classification
            res = self.board_extractor.read_board(frame)
            stones_state = self.board_classifier.read_board(res)

            if verbose:
                self.visualizer.show_cam(frame)

            # Decide what with the understood board
            is_move = self.interpreter.interpret(stones_state)

            if is_move:
                self._dump_image(frame, stones_state, exp_dir)
                self.image_ind += 1

                self.interpreter.realize_move(self.engine)
            print(time.time() - start)


        # todo unreachable code..
        cap.release()
        cv2.destroyAllWindows()
