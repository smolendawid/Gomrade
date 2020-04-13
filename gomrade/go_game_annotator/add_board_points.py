import argparse
import cv2
import yaml
import os
import numpy as np

from gomrade.classifiers.train_validate import collect_examples
from gomrade.classifiers.manual_models import ImageClicker
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

        img = cv2.imread(example)

        board_extractor_state_path = os.path.join(source, 'board_extractor_state.yml')

        if os.path.exists(board_extractor_state_path):
            continue
        print("Annotating {}".format(source))

        clicker = ImageClicker(clicks_num=4)

        img = VideoCaptureFrameMock(img)

        pts_clicks = clicker.get_points_of_interest(img, image_title='Click corners: left upper, right upper, '
                                                                     'right bottom, left bottom')

        with open(board_extractor_state_path, 'w') as f:
            yaml.safe_dump({'pts_clicks': pts_clicks}, f)

        prev_source = source
