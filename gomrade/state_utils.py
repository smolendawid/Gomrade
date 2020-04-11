import os

import cv2


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
