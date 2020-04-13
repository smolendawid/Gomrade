import argparse
import cv2
import yaml
import os
import numpy as np

from gomrade.classifiers.train_validate import collect_examples
from gomrade.classifiers.manual_models import ManualBoardStateClassifier
from gomrade.transformations import order_points

from gomrade.images_utils import VideoCaptureFrameMock


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--images_path")
    parser.add_argument("--board_size", default=19)
    args = parser.parse_args()

    board_size = args.board_size

    examples = collect_examples(args.images_path)
    prev_source = ''

    for example, source in examples:
        if source == prev_source:
            print("Skipping {}".format(source))
            continue
        print("Annotating {}".format(source))

        img = cv2.imread(example)

        board_state_classifier_state = os.path.join(source, 'board_state_classifier_state.yml')

        if os.path.exists(board_state_classifier_state):
            continue

        with open(os.path.join(source, 'board_extractor_state.yml')) as f:
            pts_clicks = yaml.load(f)['pts_clicks']

        M, max_width, max_height = order_points(np.array(pts_clicks).astype(np.float32))

        transformed_frame = cv2.warpPerspective(img, M, (max_width, max_height))
        width = transformed_frame.shape[0]
        height = transformed_frame.shape[1]

        config = {
            'board_state_classifier_state': None,
            'buffer_size': 1,
            'board_size': 19,
            'board_state_classifier': {
                'num_neighbours': 5,
            }
        }

        bsc = ManualBoardStateClassifier(width,  height)

        img = VideoCaptureFrameMock(img)
        bsc.fit(config=config, cap=img)
        bsc.dump(exp_dir=source)

        prev_source = source

