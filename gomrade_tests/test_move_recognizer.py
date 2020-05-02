import pytest
from gomrade.game_trackers import MoveRecognizer, Task
from gomrade_tests.toy_game import toy_game


def test_regular_move():
    gt = MoveRecognizer(size=9)

    stones_state = list(toy_game[0].replace(' ', ''))

    gt.replay_position(stones_state)

    assert gt.task == Task.FIRST_POSITION

    stones_state = list(toy_game[1].replace(' ', ''))

    gt.replay_position(stones_state)

    assert gt.task == Task.REGULAR

    stones_state = list(toy_game[2].replace(' ', ''))

    gt.replay_position(stones_state)

    assert gt.task == Task.REGULAR


def test_kill():
    gt = MoveRecognizer(size=9)

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
                   '. . . . . . W W .' \
                   '. . . . . W B B B'

    gt.replay_position(list(stones_state.replace(' ', '')))

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


def test_undo_to_black():
    gt = MoveRecognizer(size=9)

    for i in range(11):
        stones_state = list(toy_game[i].replace(' ', ''))
        gt.replay_position(stones_state)

    stones_state  = list(toy_game[6].replace(' ', ''))
    gt.replay_position(stones_state)

    assert gt.task == Task.UNDO
    assert gt.played.c == 'b'


def test_undo_to_white():
    gt = MoveRecognizer(size=9)

    for i in range(11):
        stones_state = list(toy_game[i].replace(' ', ''))
        gt.replay_position(stones_state)

    stones_state  = list(toy_game[7].replace(' ', ''))
    gt.replay_position(stones_state)

    assert gt.task == Task.UNDO
    assert gt.played.c == 'w'


def test_undo_and_regular():
    gt = MoveRecognizer(size=9)

    for i in range(10):
        stones_state = list(toy_game[i].replace(' ', ''))
        gt.replay_position(stones_state)

    stones_state  = list(toy_game[6].replace(' ', ''))
    gt.replay_position(stones_state)

    assert gt.task == Task.UNDO

    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . B . .' \
                   '. . . . . . . . .' \
                   '. . W B B . . . .' \
                   '. . . W . . . . .' \
                   '. . . . . . W . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .'
    gt.replay_position(list(stones_state.replace(' ', '')))

    assert gt.task == Task.REGULAR


def test_many_added():
    gt = MoveRecognizer(size=9)

    stones_state = list(toy_game[0].replace(' ', ''))
    gt.replay_position(stones_state)

    stones_state[0] = 'B'
    stones_state[1] = 'B'
    gt.replay_position(stones_state)
    assert gt.task == Task.MANY_ADDED

    stones_state[2] = 'W'
    stones_state[3] = 'W'
    gt.replay_position(stones_state)
    assert gt.task == Task.MANY_ADDED

    stones_state[4] = 'W'
    stones_state[5] = 'B'
    gt.replay_position(stones_state)

    assert gt.task == Task.MANY_ADDED


def test_disappear():
    gt = MoveRecognizer(size=9)

    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . B . B . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . W W .' \
                   '. . . . . W B B B'
    gt.replay_position(list(stones_state.replace(' ', '')))

    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . . . B . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . W W .' \
                   '. . . . . W B B B'
    gt.replay_position(list(stones_state.replace(' ', '')))

    assert gt.task == Task.DISAPPEAR


def test_other_error():
    gt = MoveRecognizer(size=9)

    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . B . B . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . W W .' \
                   '. . . . . W B B B'
    gt.replay_position(list(stones_state.replace(' ', '')))

    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . . . B . . B .' \
                   '. . . B . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . W W .' \
                   '. . . . . W B B B'
    gt.replay_position(list(stones_state.replace(' ', '')))
    assert gt.task == Task.OTHER_ERROR

    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . B B B . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .' \
                   '. . . . . . W W .' \
                   '. . . . . W B B B'
    gt.replay_position(list(stones_state.replace(' ', '')))
    assert gt.task == Task.OTHER_ERROR
