import argparse
import cv2
import yaml
import os
import numpy as np

from gomrade.classifiers.validate_full_images import collect_examples
from gomrade.classifiers.manual_models import ManualBoardExtractor
from gomrade.images_utils import VideoCaptureFrameMock


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--images_path", required=True)
    parser.add_argument("--board_size", default=19)
    args = parser.parse_args()

    board_size = args.board_size

    examples, sources = collect_examples(args.images_path)
    prev_source = ''

    for example, source in zip(examples, sources):
        if source == prev_source:
            print("Skipping {}".format(source))
            continue

        img = cv2.imread(example)

        board_extractor_state_path = os.path.join(source, 'board_extractor_state.yml')

        if os.path.exists(board_extractor_state_path):
            print("Skipping {}".format(source))
            continue
        print("Annotating {}".format(source))

        config = {
            'board_extractor_state': None,
            'board_size': int(args.board_size),
        }

        bsc = ManualBoardExtractor()

        img = VideoCaptureFrameMock(img)
        bsc.fit(config=config, cap=img)
        bsc.dump(exp_dir=source)

        prev_source = source
