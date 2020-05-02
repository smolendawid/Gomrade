import pytest


def test_system():
    """
    This test tests the entire program. The behaviour:

    Run mocked game. It makes:
    - initial position
    - a few REGULAR moves
    - stone killing
    - undo
    - regular move
    - not allowed move

    """