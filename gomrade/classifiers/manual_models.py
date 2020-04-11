import cv2
import numpy as np
import os
import yaml

from gomrade.state_utils import project_stones_state
from gomrade.transformations import order_points
from gomrade.images_utils import avg_images, get_pt_color, fill_buffer
from gomrade.classifiers.classifier import closest_color
from gomrade.classifiers.gomrade_model import GomradeModel

# todo should it be hardcoded here?
NUM_BLACK_POINTS = 2
NUM_WHITE_POINTS = 2
NUM_BOARD_POINTS = 6
PTPXL = 9


class ImageClicker:
    def __init__(self, clicks):
        self.pts_clicks = []
        self.clicks = clicks

    def _click_and_crop(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.pts_clicks.append((x, y))

    def get_points_of_interest(self, cap, image_title):

        cv2.namedWindow(image_title)
        cv2.setMouseCallback(image_title, self._click_and_crop)

        while True:
            _, frame = cap.read()

            # display the image and wait for a keypress
            cv2.imshow(image_title, frame)
            key = cv2.waitKey(1) & 0xFF

            if len(self.pts_clicks) == self.clicks:
                cv2.destroyWindow(image_title)
                break
        return self.pts_clicks


class ManualBoardStateClassifier(GomradeModel):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.black_colors = []
        self.white_colors = []
        self.board_colors = []
        self.x_grid = None
        self.y_grid = None

    def _load_from_state(self, path):
        with open(path) as f:
            data = yaml.load(f)
        self.__dict__ = data

    def _get_pt_area(self, frame, i, j):
        # c = classify_brightness(res[i, j, :], dominant_color)
        start_i = i - PTPXL
        if start_i < 0:
            start_i = 0
        stop_i = i + PTPXL
        if stop_i > frame.shape[0]:
            stop_i = frame.shape[0]

        start_j = j - PTPXL
        if start_j < 0:
            start_j = 0
        stop_j = j + PTPXL
        if stop_j > frame.shape[1]:
            stop_j = frame.shape[1]

        return frame[start_i: stop_i, start_j: stop_j, :]

    def dump(self, exp_dir):
        with open(os.path.join(exp_dir, 'board_state_classifier_state.yml'), 'w') as f:
            serialized = dict((key, value) for key, value in self.__dict__.items())
            yaml.safe_dump(serialized, f)

    def fit(self, config, cap):

        if config['board_state_classifier_state'] is not None:
            self._load_from_state(config['board_state_classifier_state'])
            return self

        num_neighbours = config['board_state_classifier']['num_neighbours']

        clicker = ImageClicker(clicks=10)
        pts_clicks = clicker.get_points_of_interest(cap, image_title='2 black, 2 white, 4 board clicks')

        buf = fill_buffer(cap, config["buffer_size"])
        frame = avg_images(buf)

        black_colors = get_pt_color(frame, pts_clicks[:2], num_neighbours=num_neighbours)
        white_colors = get_pt_color(frame, pts_clicks[:4], num_neighbours=num_neighbours)
        board_colors = get_pt_color(frame, pts_clicks[4:], num_neighbours=num_neighbours)

        # Create grid coords
        x_grid = np.floor(np.linspace(0, self.width - 1, config['board_size'])).astype(int)
        y_grid = np.floor(np.linspace(0, self.height - 1, config['board_size'])).astype(int)

        self.black_colors = [[float(p) for p in c] for c in black_colors]
        self.white_colors = [[float(p) for p in c] for c in white_colors]
        self.board_colors = [[float(p) for p in c]for c in board_colors]
        self.x_grid = [int(x) for x in x_grid]
        self.y_grid = [int(y) for y in y_grid]

    def read_board(self, frame, debug=False):
        # frame = cv2.blur(frame, ksize=(10, 10))

        stones_state = []
        for i in self.x_grid:
            for j in self.y_grid:
                area = self._get_pt_area(frame, i, j)
                mean_rgb = np.mean(np.mean(area, axis=0), axis=0)

                c = closest_color(mean_rgb, self.board_colors, self.black_colors, self.white_colors)
                stones_state.append(c)
                if debug:
                    frame[i-5: i+5, j-5: j+5, :] = 0

        return stones_state, frame


class ManualBoardExtractor(GomradeModel):
    def __init__(self):
        self.M = None
        self.max_width = None
        self.max_height = None
        self.pts_clicks = None
        self.width = None
        self.height = None

    def _load_from_state(self, path):
        with open(path) as f:
            data = yaml.load(f)
        self.__dict__ = data
        self.M = np.array(self.M)

    def dump(self, exp_dir):
        with open(os.path.join(exp_dir, 'board_extractor_state.yml'), 'w') as f:
            serialized = dict((key, value) for key, value in self.__dict__.items())
            serialized['M'] = [list(float(f) for f in m) for m in serialized['M']]
            yaml.safe_dump(serialized, f)

    def fit(self, config, cap):

        if config['board_extractor_state'] is not None:
            self._load_from_state(config['board_extractor_state'])
            return self.width, self.height

        clicker = ImageClicker(clicks=4)
        pts_clicks = clicker.get_points_of_interest(cap, image_title='Click corners: left upper, right upper, '
                                                                     'right bottom, left bottom')

        _, frame = cap.read()
        M, max_width, max_height = order_points(np.array(pts_clicks).astype(np.float32))

        self.M = M
        self.max_width = max_width
        self.max_height = max_height
        self.pts_clicks = [list(p) for p in pts_clicks]

        transformed_frame = self.read_board(frame)

        width = transformed_frame.shape[0]
        height = transformed_frame.shape[1]

        self.width = width
        self.height = height

        # todo fit should not return anything
        return width, height

    def read_board(self, frame, debug=False):
        # compute the perspective transform matrix and then apply it
        return cv2.warpPerspective(frame, self.M, (self.max_width, self.max_height))
