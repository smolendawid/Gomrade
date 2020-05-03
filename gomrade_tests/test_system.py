import cv2
import pytest
import yaml

import sys
import os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gomrade.images_utils import VideoCaptureFolderMock, VideoCaptureFrameMock
from run import init_program, load_config, setup_log


def test_system():
    """
    This test tests the entire program. The behaviour:

    Run mocked game. It makes:
    - initial position
    - a few REGULAR moves
    - stone killing
    - undo
    - regular move
    - many stones added

    """

    config = yaml.load(open('configs/system_test_config.yml', 'r'), Loader=yaml.FullLoader)
    exp_dir = 'logs/testing_sequence/'
    os.makedirs(exp_dir, exist_ok=True)

    # Cap for fitting
    frame_cap = VideoCaptureFrameMock(cv2.imread('data/sample_data/testing_sequence/0.jpg'))
    gl = init_program(config=config, exp_dir=exp_dir, cap=frame_cap)

    # Cap for the game
    cap = VideoCaptureFolderMock(images_root='data/sample_data/testing_sequence/', time_for_one_img=2)
    gl.run(cap, debug=config['debug'])

    cap.report()

    # Test whether camera mock works fine
    for freq in cap.images_freqs:
        assert freq != 0, "Each image should be used"

    # Test output sgf files
    with open(os.path.join(exp_dir, 'game.sgf')) as f:
        sgf = f.read()
    assert '(;FF[4]AB[dd][nq][pd][pp]AW[cp][do][dq][ee][ep][oe][oo]CA[UTF-8]DT' in sgf
    assert 'GM[1]KM[6.5]SZ[19];B[gp])' in sgf

    with open(os.path.join(exp_dir, 'game1.sgf')) as f:
        sgf = f.read()
    assert 'GM[1]KM[6.5]SZ[19];B[dp];W[do];B[pp];W[ep];B[pd];' in sgf
    assert 'W[cp];B[dd];W[dq];B[nq])' in sgf
