import logging
import time
import warnings

import numpy as np


class BoardStateInterpreter:
    def __init__(self, config):
        warnings.warn("BoardStateInterpreter is hardware dependent and should not be used anymore!")

        self.num_of_the_same = 0
        self.num_of_the_diff = 0
        self.artifact = 0
        self.trigger = False
        self.prev_stones_state = np.zeros((config['board_size'] * config['board_size'],))

        self.artifact_limit = config['artifact_limit']
        self.move_limit = config['move_limit']
        self.accept_limit = config['accept_limit']

    def interpret(self, stones_state, color_to_play):

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
        if color_to_play == 'w':
            tmp_limit = self.move_limit
        elif color_to_play == 'b':
            tmp_limit = self.accept_limit
        else:
            raise ValueError("Wrong color")

        if self.num_of_the_same > tmp_limit:
            if self.trigger:

                self.num_of_the_same = 0
                self.trigger = False
                logging.info("MOVE MADE")
                is_move = True

        return is_move


class TimeBoardStateInterpreter:
    def __init__(self, config):
        """ Objects analyses time and the changes in recognized board state. Works this way:
        - If board state changed, check for `self.minimal_duration` if it's still the same. If not, ignore, if yes,
        consider it as a real change. Trigger the object
        - If state is `self.move_acceptance` long the same, and object is triggered, decide the move has been made

        :param config:
        """
        self.prev_stones_state = np.chararray((config['board_size'] * config['board_size'],))
        self.minimal_duration = config['minimal_duration_time']
        self.move_acceptance = config['move_acceptance_time']
        self.curr_dur = 0.
        self.last_move_last_seen = time.time()
        self.is_still = 0.
        self.prev_time = 0.
        if config["ai_color"] == config["to_move"]:
            self.triggered = True
        else:
            self.triggered = False

    def _check_state_the_same(self, stones_state):
        is_same = False
        if len(stones_state) == sum([1 for i, j in zip(stones_state, self.prev_stones_state) if i == j]):
            is_same = True
        return is_same

    def interpret(self, stones_state: list, color_to_play) -> bool:
        is_move = False
        curr = time.time()

        is_state_same = self._check_state_the_same(stones_state)

        if is_state_same:
            self.last_move_last_seen = curr
            self.is_still += (curr - self.prev_time)
        else:
            self.is_still = 0.
            if curr - self.last_move_last_seen > self.minimal_duration:
                # Update state
                self.prev_stones_state = stones_state
                self.triggered = True

        if self.triggered:
            if self.is_still > self.move_acceptance:
                self.last_move_last_seen = curr
                self.triggered = False
                is_move = True

        self.prev_time = curr

        return is_move