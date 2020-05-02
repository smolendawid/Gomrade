import argparse
import os
import yaml
import logging
import cv2
from datetime import datetime

from gtp.talker import GTPFacade
from gomrade.gomrade_game import GomradeGame
from gomrade.classifiers.manual_models import ManualBoardExtractor
from gomrade.state_visualizer import StateVisualizer, show_board_with_grid
from utils.dynamic_import import dynamic_import


def setup_log(root='logs'):
    os.makedirs(root, exist_ok=True)
    now = datetime.now()
    current_time = now.strftime("%y_%m_%d_%H_%M_%S")
    exp_dir = os.path.join(root, f'{current_time}')
    os.mkdir(exp_dir)

    return exp_dir


def setup_engine(config):

    # GNUGO_LEVEL_ONE = ["gnugo", "--mode", "gtp", "--level", "1"]
    # katago gtp -config $(brew list --verbose katago | grep gtp) -model $(brew list --verbose katago | grep .gz | head -1)

    engine = GTPFacade(label='game', args=config['engine_command'])

    engine.name()
    engine.version()

    engine.boardsize(config['board_size'])
    engine.komi(config['komi'])

    return engine


def load_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default='configs/config.yml')
    args = parser.parse_args()

    return yaml.load(open(args.config, 'r'))


def init_program(config, exp_dir, cap):

    engine = setup_engine(config=config)

    be = ManualBoardExtractor(enlarge=True, resample=True)
    be.fit(config=config, cap=cap)

    # Show example board
    ret, frame = cap.read()
    res, x_grid, y_grid = be.read_board(frame)
    show_board_with_grid(res, x_grid, y_grid)

    bsc = dynamic_import(config['board_state_classifier']['name'])()
    bsc.fit(config=config, cap=cap)

    vis = StateVisualizer()

    gl = GomradeGame(config=config, exp_dir=exp_dir, engine=engine,
                     board_extractor=be, board_classifier=bsc, visualizer=vis)

    return gl


if __name__ == '__main__':

    config = load_config()
    exp_dir = setup_log()
    cap = cv2.VideoCapture(0)

    gl = init_program(config=config, exp_dir=exp_dir, cap=cap)

    gl.run(cap, debug=config['debug'])
