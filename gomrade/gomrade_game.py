import os
import subprocess
import time
import cv2
import warnings
import logging
# import simpleaudio as sa

from gomrade.images_utils import avg_images_in_buffer, fill_buffer
from gomrade.state_utils import save_game_state
from gomrade.action_interpreters import TimeBoardStateInterpreter
from gomrade.game_trackers import SgfTranslator, Task
from gomrade.classifiers.gomrade_model import GomradeExtractor
from gomrade.common import Move


def play_wav(m):
    """ Move value. Can be GO board coordinates, 'resign', and 'pass'"""
    try:
        subprocess.call(["afplay", 'data/synthesized_moves/{}.mp3'.format(m)])
        # wave_obj = sa.WaveObject.from_wave_file('data/synthesized_moves/{}.mp3'.format(m))
        # wave_obj.play()

    except ResourceWarning:
        warnings.warn("Unable to play sound {}.mp3".format(m))


class GomradeGame:
    def __init__(self, config: dict, exp_dir: str, engine, board_extractor: GomradeExtractor,
                 board_classifier, visualizer):
        """
        The main class of the project. It uses objects to analyse crop board, classify it, and, considering defined
        logic, communicate with GTP engine.

        :param config: .yml as in example config
        :param exp_dir:
        :param engine: GTP engine
        :param board_extractor:
        :param board_classifier:
        :param visualizer: Object that will visualize the current interpretation and understanding of the board
        """

        self.buffer_size = config['buffer_size']
        self.ai_color = config['ai_color']
        self.exp_dir = exp_dir
        self.sgf_file_root = exp_dir

        self.engine = engine
        self.visualizer = visualizer
        self.board_extractor = board_extractor
        self.board_classifier = board_classifier
        self.interpreter = TimeBoardStateInterpreter(config=config)
        self.sgf_translator = SgfTranslator(config['board_size'], komi=config['komi'], root_path=self.sgf_file_root)

        self.sleep = config['sleep_between_frames']
        self.move = Move(first_move=config['ai_color'])

        self.image_ind = 0

    def _execute(self, engine, stones_state):

        task = self.sgf_translator.parse(stones_state)

        if task == Task.OTHER_ERROR: play_wav('error')
        if task == Task.UNDO: play_wav('undo')
        if task == Task.DISAPPEAR: play_wav('disappeared')
        if task != Task.UNDO and task != Task.REGULAR and task != Task.KILL: play_wav('reset')

        engine.clear_board()
        engine.load_sgf(path=self.sgf_translator.path)
        engine.showboard()

    def _execute_move(self, engine, stones_state):
        if self.move.c == self.ai_color:
            logging.info('Asking for a move')

            self._execute(engine, stones_state)

            vertex = engine.genmove(self.move.c)
            play_wav(vertex)

        else:
            logging.info('Doing nothing')

            play_wav('move')
            self._execute(engine, stones_state)

    def run(self, cap, debug=True):

        buf_i = 0

        # fill images buffer
        buf = fill_buffer(cap, self.buffer_size)

        global_start = time.time()

        while True:
            time.sleep(self.sleep)
            start = time.time()

            # Capture frame-by-frame
            ret, frame = cap.read()

            # Average images for homogeneous colors
            buf[buf_i] = frame
            buf_i = (buf_i + 1) % self.buffer_size
            frame = avg_images_in_buffer(buf)

            # Crop image to board and perform classification
            res, x_grid, y_grid = self.board_extractor.read_board(frame, debug=debug)

            stones_state, res = self.board_classifier.read_board(res, x_grid, y_grid, debug=debug)

            if debug:
                self.visualizer.show_cam(res)

            # Decide what to do with the understood board
            is_move = self.interpreter.interpret(stones_state, self.move.c)

            if is_move:
                save_game_state(frame, stones_state, exp_dir=self.exp_dir, name=self.image_ind)
                self.image_ind += 1

                self.move.switch()
                self._execute_move(self.engine, stones_state)
            # print(time.time() - start)
            if debug:
                if time.time() - global_start > 100:
                    break

        # todo unreachable code..
        cap.release()
        cv2.destroyAllWindows()
