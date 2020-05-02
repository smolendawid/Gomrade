from collections import Counter

from gomrade.game_trackers import SgfTranslator, Task
from gomrade_tests.toy_game import toy_game


def test_regular_game():
    sgf_file_root = '../gomrade_tests/'
    sgf_translator = SgfTranslator(board_size=9, komi=0.5, root_path=sgf_file_root)

    sgf_translator.create_empty()
    for i in range(13):
        stones_state = list(toy_game[i].replace(' ', ''))
        task = sgf_translator.parse(stones_state)

    with open('../gomrade_tests/game.sgf') as f:
        game_str = f.read()
    assert 'AW' or 'AB' not in game_str


def test_error_game():
    sgf_file_root = '../gomrade_tests/'
    sgf_translator = SgfTranslator(board_size=9, komi=0.5, root_path=sgf_file_root)

    sgf_translator.create_empty()
    for i in range(13):
        stones_state = list(toy_game[i].replace(' ', ''))
        task = sgf_translator.parse(stones_state)

    stones_state = 'B B B . . . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . B . .' \
                   '. . W W . . . . .' \
                   '. . W B . . . . .' \
                   '. . . W B . . . .' \
                   '. . . B . . W . .' \
                   '. . . . . W W W .' \
                   '. . . . . . . . .'

    task = sgf_translator.parse(list(stones_state.replace(' ', '')))

    with open('../gomrade_tests/game.sgf') as f:
        game_str = f.read()
    assert 'AW' or 'AB' in game_str

    stones_state = 'B B B . . . . . .' \
                   '. . . B . . . . .' \
                   '. . . . W . B . .' \
                   '. . W W . . . . .' \
                   '. . W B . . . . .' \
                   '. . . W B . . . .' \
                   '. . . B . . W . .' \
                   '. . . . . W W W .' \
                   '. . . . . . . . .'

    task = sgf_translator.parse(list(stones_state.replace(' ', '')))

    stones_state = 'B B B . . . . . .' \
                   '. . . B . . . . .' \
                   '. . . . W . B . .' \
                   '. . W W . . B . .' \
                   '. . W B . . . . .' \
                   '. . . W B . . . .' \
                   '. . . B . . W . .' \
                   '. . . . . W W W .' \
                   '. . . . . . . . .'

    task = sgf_translator.parse(list(stones_state.replace(' ', '')))

    with open('../gomrade_tests/game.sgf') as f:
        game_str = f.read()
    assert 'AW' or 'AB' in game_str
    assert ';W' or ';B' in game_str


def test_undo():
    sgf_file_root = '../gomrade_tests/'
    sgf_translator = SgfTranslator(board_size=9, komi=0.5, root_path=sgf_file_root)

    sgf_translator.create_empty()
    for i in range(13):
        stones_state = list(toy_game[i].replace(' ', ''))
        task = sgf_translator.parse(stones_state)

    stones_state = list(toy_game[6].replace(' ', ''))
    task = sgf_translator.parse(stones_state)
    assert task == Task.UNDO

    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . B . .' \
                   '. . . . . . . . .' \
                   '. . W B B . . . .' \
                   '. . . W . . . . .' \
                   '. . . . . . W . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .'

    task = sgf_translator.parse(list(stones_state.replace(' ', '')))
    assert task == Task.REGULAR

    with open('../gomrade_tests/game.sgf') as f:
        game_str = f.read()
    assert ';W' or ';B' in game_str

    counter = Counter(game_str)

    assert counter['('] == 3
    assert counter[')'] == 3


def test_double_undo_to_main_sequence():
    sgf_file_root = '../gomrade_tests/'
    sgf_translator = SgfTranslator(board_size=9, komi=0.5, root_path=sgf_file_root)

    sgf_translator.create_empty()
    for i in range(13):
        stones_state = list(toy_game[i].replace(' ', ''))
        task = sgf_translator.parse(stones_state)

    stones_state = list(toy_game[6].replace(' ', ''))
    task = sgf_translator.parse(stones_state)
    assert task == Task.UNDO

    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . B . .' \
                   '. . . . . . . . .' \
                   '. . W B B . . . .' \
                   '. . . W . . . . .' \
                   '. . . . . . W . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .'

    task = sgf_translator.parse(list(stones_state.replace(' ', '')))
    assert task == Task.REGULAR

    stones_state = list(toy_game[5].replace(' ', ''))
    task = sgf_translator.parse(stones_state)
    assert task == Task.UNDO

    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . B . .' \
                   '. . . . . . . . .' \
                   '. . . B . . W . .' \
                   '. . . W . . . . .' \
                   '. . . . . . W . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .'

    task = sgf_translator.parse(list(stones_state.replace(' ', '')))
    assert task == Task.REGULAR

    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . B . .' \
                   '. . . . . . . B .' \
                   '. . . B . . W . .' \
                   '. . . W . . . . .' \
                   '. . . . . . W . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .'

    task = sgf_translator.parse(list(stones_state.replace(' ', '')))
    assert task == Task.REGULAR


def test_undo_to_previoius_tree():
    sgf_file_root = '../gomrade_tests/'
    sgf_translator = SgfTranslator(board_size=9, komi=0.5, root_path=sgf_file_root)

    sgf_translator.create_empty()
    for i in range(13):
        stones_state = list(toy_game[i].replace(' ', ''))
        task = sgf_translator.parse(stones_state)

    # Back to white move
    stones_state = list(toy_game[6].replace(' ', ''))
    task = sgf_translator.parse(stones_state)
    assert task == Task.UNDO

    # Different blacks move
    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . B . .' \
                   '. . . . . . . . .' \
                   '. . W B B . . . .' \
                   '. . . W . . . . .' \
                   '. . . . . . W . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .'

    task = sgf_translator.parse(list(stones_state.replace(' ', '')))
    assert task == Task.REGULAR

    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . B . .' \
                   '. . . . . . . . .' \
                   '. . W B B . W . .' \
                   '. . . W . . . . .' \
                   '. . . . . . W . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .'

    # white response
    task = sgf_translator.parse(list(stones_state.replace(' ', '')))
    assert task == Task.REGULAR

    # black move again
    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . B . .' \
                   '. . . . . . . . .' \
                   '. . W B B . W . .' \
                   '. . . W B . . . .' \
                   '. . . . . . W . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .'

    task = sgf_translator.parse(list(stones_state.replace(' ', '')))
    assert task == Task.REGULAR

    # White response again
    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . B . .' \
                   '. . . . . . . . .' \
                   '. . W B B . W . .' \
                   '. . W W B . . . .' \
                   '. . . . . . W . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .'

    task = sgf_translator.parse(list(stones_state.replace(' ', '')))
    assert task == Task.REGULAR

    # Undo last black decision
    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . B . .' \
                   '. . . . . . . . .' \
                   '. . W B B . W . .' \
                   '. . . W . . . . .' \
                   '. . . . . . W . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .'


    task = sgf_translator.parse(list(stones_state.replace(' ', '')))
    assert task == Task.UNDO


    # Blacks better move
    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . B . .' \
                   '. . . . . . . . .' \
                   '. . W B B . W . .' \
                   '. . B W . . . . .' \
                   '. . . . . . W . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .'

    task = sgf_translator.parse(list(stones_state.replace(' ', '')))
    assert task == Task.REGULAR

    # White answers
    stones_state = '. . . . . . . . .' \
                   '. . . B . . . . .' \
                   '. . . . . . B . .' \
                   '. . . . . . . . .' \
                   '. . W B B . W . .' \
                   '. . B W . . . . .' \
                   '. . W . . . W . .' \
                   '. . . . . . . . .' \
                   '. . . . . . . . .'

    task = sgf_translator.parse(list(stones_state.replace(' ', '')))
    assert task == Task.REGULAR

    with open('../gomrade_tests/game.sgf') as f:
        game_str = f.read()
    assert ';W' or ';B' in game_str
    assert 'AW' or 'AB' in game_str

    counter = Counter(game_str)

    assert counter['('] == 5
    assert counter[')'] == 5
