import os
import cv2

import numpy as np
import math


def create_pretty_state(stones_state):
    result = ''
    board_size = int(math.sqrt(len(stones_state)))

    for x in range(board_size):
        if x != 0:
            result += '\n'
        for y in range(board_size):
            result += str(stones_state[x * board_size + y])
            if y != board_size - 1:
                result += ' '

    return result


def write_pretty_state(stones_state, path, debug=False):
    """ Write stones state in readable format"""

    result = create_pretty_state(stones_state)

    if debug:
        print(result)

    with open(path, 'w') as f:
        f.write(result)


def save_game_state(frame, stones_state, exp_dir, name):
    """Save the image and stones state"""
    cv2.imwrite(os.path.join(exp_dir, f"{name}.png"), frame)
    write_pretty_state(stones_state, path=os.path.join(exp_dir, "{}.txt".format(name)))


def project_stones_state(stones_state: list, flip: bool = True, rotate: bool = True):
    """ todo should allow combinations of flip and rotate orde
    :param stones_state: list of N = board_size*board_size characters
    :param flip: left to right flip
    :param rotate: upside-down rotation
    :return: stones_state after transformation
    """
    if rotate and flip:
        stones_state = stones_state[::-1]
    elif not rotate and flip:
        size = int(math.sqrt(len(stones_state)))
        stones_state = np.reshape(stones_state, (size, -1)).T[::-1].T.flatten()
        stones_state = ''.join(list(stones_state))
    elif rotate and not flip:
        size = int(math.sqrt(len(stones_state)))
        stones_state = np.reshape(stones_state, (size, -1))[::-1].flatten()
        stones_state = ''.join(list(stones_state))
    else:
        pass

    return stones_state

