import argparse
import cv2
import yaml
import os
import numpy as np

from gomrade.classifiers.validate_full_images import collect_examples
from gomrade.classifiers.manual_models import ManualBoardStateClassifier, ManualBoardExtractor
from gomrade.transformations import order_points

from gomrade.images_utils import VideoCaptureFrameMock


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--images_path")
    parser.add_argument("--board_size", default=19)
    args = parser.parse_args()

    board_size = args.board_size

    examples, sources = collect_examples(args.images_path)
    prev_source = ''

    for example, source in zip(examples, sources):
        if source == prev_source:
            if os.path.exists(os.path.join(source, 'board_state_classifier_state.yml')):
                continue

        img = cv2.imread(example)

        board_state_classifier_state = os.path.join(source, 'board_state_classifier_state.yml')

        if os.path.exists(board_state_classifier_state):
            print("Skipping {}".format(source))
            continue

        print("Annotating {}".format(source))

        config = {
            'board_extractor_state': os.path.join(source, 'board_extractor_state.yml'),
            'board_state_classifier_state': None,
            'board_size': 19,
            'buffer_size': 3,
            'board_state_classifier': {
                'num_neighbours': 5,
            }
        }

        cap = VideoCaptureFrameMock(img)

        mbe = ManualBoardExtractor(resample=True)
        mbe.fit(config=config, cap=cap)

        _, frame = cap.read()
        res, x_grid, y_grid = mbe.read_board(frame, debug=False)

        bsc = ManualBoardStateClassifier()
        bsc.fit(config=config, cap=cap)

        if len(bsc.black_colors) != 0:
            bsc.dump(exp_dir=source)

        prev_source = source

