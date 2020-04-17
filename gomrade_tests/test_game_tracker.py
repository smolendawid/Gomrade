import pytest
from gomrade.game_trackers import GameTracker, Task
from gomrade_tests.toy_game import toy_game


def _init():
    gt = GameTracker()
    gt.create_empty(size=9, komi=0.5)
    return gt


def test_regular_move():
    gt = _init()

    stones_state = list(toy_game[0].replace(' ', ''))

    gt.replay_position(stones_state)

    assert gt.task == Task.REGULAR

    stones_state = list(toy_game[1].replace(' ', ''))

    gt.replay_position(stones_state)

    assert gt.task == Task.REGULAR


def test_kill():
    gt = _init()


    stones_state = list(toy_game[9].replace(' ', ''))
    gt.replay_position(stones_state)

    stones_state = list(toy_game[10].replace(' ', ''))
    gt.replay_position(stones_state)

    assert gt.task == Task.KILL

    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . B . B . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . W W W' \
                   '. . . . . W . . .'

    gt.replay_position(list(stones_state.replace(' ', '')))

    assert gt.task == Task.KILL


def test_undo():
    gt = _init()

    for i in range(10):
        stones_state = list(toy_game[i].replace(' ', ''))
        gt.replay_position(stones_state)

    stones_state  = list(toy_game[5].replace(' ', ''))
    gt.replay_position(stones_state)

    assert gt.task == Task.UNDO
