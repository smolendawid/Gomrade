import subprocess
import time
import cv2
import warnings

from gomrade.images_utils import avg_images, fill_buffer
from gomrade.save_game_state import save_game_state
from gomrade.action_interpreters import TimeBoardStateInterpreter
from gomrade.game_trackers import GameTracker


def play_wave(m):
    """ Move value. Can be GO board coordinates, 'resign', or 'pass'"""
    # todo afplay is of MAC
    # todo mp3 is hard to play in python
    try:
        subprocess.call(["afplay", f'data/synthetized_moves/{m}.mp3'])
    except ResourceWarning:
        warnings.warn("Unable to play sound {}.mp3".format(m))


class Move:
    def __init__(self, first_move):
        self._c = first_move

    def switch(self):
        if self._c == 'black':
            self._c = 'white'
        else:
            self._c = 'black'

    @property
    def c(self):
        return self._c


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
        self.interpreter = TimeBoardStateInterpreter(config=config)
        self.game_tracker = GameTracker(tmp_path='data/tmp.txt')

        self.move = Move(first_move=config['ai_color'])

        self.image_ind = 0

    def _execute_move(self, engine, stones_state):
        if self.move.c == 'black':
            print('Asking for a move')
            engine.clear_board()
            self.game_tracker.replay_position(stones_state)
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
            is_move = self.interpreter.interpret(stones_state, self.move.c)

            if is_move:
                save_game_state(frame, stones_state, board_size=self.board_size, exp_dir=exp_dir, name=self.image_ind)
                self.image_ind += 1

                self.move.switch()
                self._execute_move(self.engine, stones_state)
            # print(time.time() - start)

        # todo unreachable code..
        cap.release()
        cv2.destroyAllWindows()
