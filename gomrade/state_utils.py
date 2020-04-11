import os
import cv2

import numpy as np
import math


def _write_pretty_state(stones_state, board_size, exp_dir, name):

    with open(os.path.join(exp_dir, f"{name}.txt"), 'w') as f:
        for x in range(board_size):
            if x != 0:
                f.write('\n')
            for y in range(board_size):
                f.write(str(stones_state[x * board_size + y]))
                if y != board_size - 1:
                    f.write(' ')


def save_game_state(frame, stones_state, board_size, exp_dir, name):
    cv2.imwrite(os.path.join(exp_dir, f"{name}.png"), frame)
    _write_pretty_state(stones_state, board_size, exp_dir, name)


def project_stones_state(stones_state: str, flip: bool = True, rotate: bool = True):
    """
    :param stones_state: string of N = board_size*board_size characters
    :param flip: left to right flip
    :param rotate: upside-down rotation
    :return: stones_state after transformation
    """
    if rotate and flip:
        stones_state = stones_state[::-1]
    elif not rotate and flip:
        # size = int(math.sqrt(len(stones_state)))
        # stones_state = np.reshape(stones_state, (size, -1))
        raise NotImplementedError()
    elif rotate and not flip:
        size = int(math.sqrt(len(stones_state)))
        stones_state = np.reshape(stones_state, (size, -1))[::-1].flatten()
        stones_state = ''.join(list(stones_state))
    else:
        pass

    return stones_state

