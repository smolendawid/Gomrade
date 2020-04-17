import pytest
from gomrade.gomrade_game import play_wav


def test_play_wav():
    play_wav('A3')
    assert True
