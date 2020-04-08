import numpy as np


class BoardStateInterpreter:
    def __init__(self, config):
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
        if color_to_play == 'white':
            tmp_limit = self.move_limit
        elif color_to_play == 'black':
            tmp_limit = self.accept_limit
        else:
            raise ValueError("Wrong color")

        if self.num_of_the_same > tmp_limit:
            if self.trigger:

                self.num_of_the_same = 0
                self.trigger = False
                print("MOVE MADE")
                is_move = True

        return is_move


class TimeActionInterpreter:
    def __init__(self, config):
        pass
