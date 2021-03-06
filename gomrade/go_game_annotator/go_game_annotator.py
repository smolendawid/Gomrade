import argparse

import cv2
import tqdm
import yaml
import os
import numpy as np

from gomrade.classifiers.keras_model import KerasModel
from gomrade.classifiers.manual_models import ManualBoardExtractor
from gomrade.state_utils import project_stones_state, write_pretty_state, create_pretty_state
from gomrade.transformations import order_points
from gomrade.images_utils import VideoCaptureFrameMock
from gomrade.common import collect_examples

MODEL_PATH = '/Users/dasm/projects/Gomrade/data/go_model.h5'


class ImageClickerChange:
    def __init__(self, clicks_num=None):
        """ object for collecting the clicks on image
        If clicks_num == None it saves points until 'q' is clicked"""

        self.pt0 = None
        self.pt1 = None
        self.clicks_num = clicks_num
        self.user_changes = {}
        self.prev_state = '.'*361
        self.mgx, self.mgy = None, None

    def _click_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.pt0 = [x, y]
        if event == cv2.EVENT_LBUTTONUP:
            self.pt1 = [x, y]

    def _change_state_to_next(self, stones_state, i):

        if stones_state[i] == '.':
            stones_state[i] = 'B'
        elif stones_state[i] == 'B':
            stones_state[i] = 'W'
        elif stones_state[i] == 'W':
            stones_state[i] = '.'

        return stones_state

    def modify(self, frame, stones_state, x_grid, y_grid, board_size):
        stones_state = self.apply_user_changes(stones_state)
        changed_state = stones_state.copy()

        image_title = "accept or change colors"
        cv2.namedWindow(image_title)
        cv2.setMouseCallback(image_title, self._click_event)
        self.mgx, self.mgy = np.meshgrid(x_grid, y_grid)

        circle_size = 3
        while True:
            for i, col in enumerate(y_grid):
                for j, row in enumerate(x_grid):
                    curr = stones_state[i*board_size + j]
                    prev = self.prev_state[i*board_size + j]
                    if curr != prev:
                        cv2.circle(frame, (col, row), circle_size+1, (0, 255, 0), circle_size)

                    if curr == 'W':
                        cv2.circle(frame, (col, row), circle_size, (255, 255, 255), -1)
                    if curr == 'B':
                        cv2.circle(frame, (col, row), circle_size, (0, 0, 0), -1)
                    if curr == '.':
                        cv2.circle(frame, (col, row), circle_size, (206, 26, 226), -1)

            # display the image and wait for a keypress
            cv2.imshow(image_title, frame)
            if cv2.waitKey(33) == ord('q'):
                cv2.destroyWindow(image_title)
                break

            if self.pt0 is not None and self.pt1 is not None:
                # Are close
                if abs(self.pt1[0] - self.pt0[0]) < 50 and abs(self.pt1[1] - self.pt0[1]) < 50:
                    i = closest(self.mgx, self.mgy, self.pt0)
                    stones_state = self._change_state_to_next(stones_state, i)

                else:
                    indices = in_area(self.mgx, self.mgy, self.pt0, self.pt1)
                    for i in indices:
                        stones_state = self._change_state_to_next(stones_state, i)

                        # self.idx_changed.add(i)
                self.pt0 = None
                self.pt1 = None

        for i, (prev, curr) in enumerate(zip(changed_state, stones_state)):
            if prev != curr:
                self.user_changes[i] = curr
        self.prev_state = stones_state

        return stones_state

    def apply_user_changes(self, stones_state):
        for i, val in self.user_changes.items():
            stones_state[i] = val
        return stones_state


def in_area(mgx, mgy, pt0, pt1):
    indices = []
    for i, (x, y) in enumerate(zip(mgx.flatten(), mgy.flatten())):
        if x > pt0[1] and y < pt0[0] and x < pt1[1] and y > pt1[0]:
            indices.append(i)
    return indices


def closest(mgx, mgy, point):
    min_i = None
    min = 10000000
    for i, (x, y) in enumerate(zip(mgx.flatten(), mgy.flatten())):
        dist = np.square(point[0] - y) + np.square(point[1] - x)
        if dist < min:
            min_i = i
            min = dist

    return min_i


def _create_annotation(annotation_path, stones_state):
    stones_state = np.reshape(np.array(stones_state), (-1, 19)).T.flatten()
    stones_state = ''.join(stones_state.tolist())

    write_pretty_state(stones_state, path=annotation_path, debug=True)


def _load_params_for_source(img, board_extractor_state_path):
    with open(board_extractor_state_path) as f:
        pts_clicks = yaml.load(f)['pts_clicks']

    M, max_width, max_height = order_points(np.array(pts_clicks).astype(np.float32))
    img_transformed = cv2.warpPerspective(img, M, (max_width, max_height))

    width = img_transformed.shape[0]
    height = img_transformed.shape[1]

    x_grid = np.floor(np.linspace(0, width - 1, board_size)).astype(int)
    y_grid = np.floor(np.linspace(0, height - 1, board_size)).astype(int)
    x_grid = [int(x) for x in x_grid]
    y_grid = [int(y) for y in y_grid]

    img = cv2.warpPerspective(img, M, (max_width, max_height))

    return x_grid, y_grid, img


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--images_path", required=True)
    parser.add_argument("--board_size", default=19)
    args = parser.parse_args()

    board_size = int(args.board_size)

    examples, sources = collect_examples(args.images_path)

    x_grid, y_grid, img = None, None, None
    prev_source = ''
    ic = ImageClickerChange()

    for example, source in tqdm.tqdm(zip(examples, sources)):

        annotation_path = example[:-4] + '.txt'
        if os.path.exists(annotation_path):
            continue

        print('Annotating: {}'.format(example))

        img = cv2.imread(example)

        config = {
            'board_extractor_state': os.path.join(source, 'board_extractor_state.yml'),
            'board_state_classifier': os.path.join(source, 'board_state_classifier_state.yml'),
            'board_size': 19,
        }
        cap = VideoCaptureFrameMock(img)
        mbe = ManualBoardExtractor(resample=True, enlarge=True)
        mbe.fit(config=config, cap=cap)
        bsc = KerasModel(MODEL_PATH)
        # bsc = ManualBoardStateClassifier()

        bsc.fit(config=None, cap=cap)

        _, frame = cap.read()
        res, x_grid, y_grid = mbe.read_board(frame, debug=False)
        stones_state, res = bsc.read_board(res, x_grid, y_grid, debug=False)

        # stones_state = project_stones_state(stones_state, rotate=False)
        stones_state = np.reshape(np.array(stones_state), (-1, 19)).T.flatten()

        stones_state = ic.modify(res, stones_state, x_grid, y_grid, board_size)

        _create_annotation(annotation_path, stones_state)

        prev_source = source
