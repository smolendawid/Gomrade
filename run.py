import os
import yaml
import logging
import cv2
from datetime import datetime

from gtp.talker import GTPFacade
from gomrade.gomrade_game import GomradeGame
from gomrade.state_visualizer import StateVisualizer
from utils.dynamic_import import dynamic_import


GNUGO = ["gnugo", "--mode", "gtp"]
GNUGO_LEVEL_ONE = ["gnugo", "--mode", "gtp", "--level", "1"]
GNUGO_MONTE_CARLO = ["gnugo", "--mode", "gtp", "--monte-carlo"]

KATAGO = ["katago", "gtp", "-config", "/usr/local/Cellar/katago/1.3.5/share/katago/configs/gtp_example.cfg", "-model",
          "/usr/local/Cellar/katago/1.3.5/share/katago/g170-b40c256x2-s2383550464-d716628997.bin.gz"]
# todo make it work with best model despite of the localisation
# KATAGO = ["katago gtp -config $(brew list --verbose katago | grep gtp) "
#           "-model $(brew list --verbose katago | grep .gz | head -1)"]
# katago gtp -config $(brew list --verbose katago | grep gtp) -model $(brew list --verbose katago | grep .gz | head -1)


def setup_log():
    now = datetime.now()
    current_time = now.strftime("%y_%m_%d_%H_%M_%S")
    exp_dir = f'logs/{current_time}'
    os.mkdir(exp_dir)

    return exp_dir


def setup_engine(config):

    engine = GTPFacade(label='game', args=KATAGO)

    engine.name()
    engine.version()

    engine.boardsize(config['board_size'])

    engine.komi(config['komi'])

    engine.clear_board()
    engine.showboard()

    return engine


if __name__ == '__main__':

    config = yaml.load(open('config.yml', 'r'))
    exp_dir = setup_log()

    engine = setup_engine(config=config)

    cap = cv2.VideoCapture(0)

    be = dynamic_import(config['board_extractor']['name'])()
    width, height = be.fit(config=config, cap=cap)

    bsc = dynamic_import(config['board_state_classifier']['name'])(width, height)  # todo anyway to do it in less ugly?
    bsc.fit(config=config, cap=cap)

    be.dump(exp_dir=exp_dir)
    bsc.dump(exp_dir=exp_dir)

    vis = StateVisualizer()

    gl = GomradeGame(config=config, engine=engine, board_extractor=be, board_classifier=bsc, visualizer=vis)
    gl.run(cap, exp_dir)
