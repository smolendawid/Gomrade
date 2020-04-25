import cv2
import numpy as np
import os
import yaml

from gomrade.state_utils import project_stones_state
from gomrade.transformations import order_points
from gomrade.images_utils import avg_images_in_buffer, get_pt_color, fill_buffer
from gomrade.classifiers.classifier import closest_color
from gomrade.classifiers.gomrade_model import GomradeModel

# todo should it be hardcoded here?
NUM_BLACK_POINTS = 2
NUM_WHITE_POINTS = 2
NUM_BOARD_POINTS = 6
PTPXL = 9


class ImageClicker:
    def __init__(self, clicks_num=None):
        """ object for collecting the clicks on image
        If clicks_num == None it saves points until 'q' is clicked"""

        self.pts_clicks = []
        self.clicks_num = clicks_num

    def _click_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.pts_clicks.append((x, y))

    def get_points_of_interest(self, obj, image_title: str):
        """ Get points from VideoCaputre or frame
        :param obj: VideoCapture
        :param image_title: str
        :return: list of self.clicks_num coordinates [(x,y), ...]
        """

        cv2.namedWindow(image_title)
        cv2.setMouseCallback(image_title, self._click_event)

        while True:
            _, frame = obj.read()

            # display the image and wait for a keypress
            cv2.imshow(image_title, frame)
            if cv2.waitKey(33) == ord('q'):
                cv2.destroyWindow(image_title)
                break
            for pt in self.pts_clicks:
                cv2.circle(frame,(pt[0], pt[1]), 5, (0,255,0), -1)

            if len(self.pts_clicks) == self.clicks_num:
                cv2.destroyWindow(image_title)
                break
        return self.pts_clicks


class ManualBoardStateClassifier():
    def __init__(self):
        self.black_colors = []
        self.white_colors = []
        self.board_colors = []

    def _load_from_state(self, path):
        with open(path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
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

        clicker = ImageClicker(clicks_num=10)
        pts_clicks = clicker.get_points_of_interest(cap, image_title='2 black, 2 white, 4 board clicks')

        buf = fill_buffer(cap, config["buffer_size"])
        frame = avg_images_in_buffer(buf)

        black_colors = get_pt_color(frame, pts_clicks[:2], num_neighbours=num_neighbours)
        white_colors = get_pt_color(frame, pts_clicks[2:4], num_neighbours=num_neighbours)
        board_colors = get_pt_color(frame, pts_clicks[4:], num_neighbours=num_neighbours)

        self.black_colors = [[float(p) for p in c] for c in black_colors]
        self.white_colors = [[float(p) for p in c] for c in white_colors]
        self.board_colors = [[float(p) for p in c]for c in board_colors]

    def read_board(self, frame, x_grid, y_grid, debug=False):
        # frame = cv2.blur(frame, ksize=(10, 10))

        stones_state = []
        for i in x_grid:
            for j in y_grid:
                area = self._get_pt_area(frame, i, j)
                mean_rgb = np.mean(np.mean(area, axis=0), axis=0)

                c = closest_color(mean_rgb, self.board_colors, self.black_colors, self.white_colors)
                stones_state.append(c)
                if debug:
                    frame[i-5: i+5, j-5: j+5, :] = 0

        return stones_state, frame


class ManualBoardExtractor(GomradeModel):
    def __init__(self, resample=False, enlarge=False):
        self.M = None
        self.max_width = None
        self.max_height = None
        self.pts_clicks = None
        self.width = None
        self.height = None
        self.x_grid = None
        self.y_grid = None

        self.enlarge = enlarge
        self.resample = resample

    def _load_from_state(self, path):
        with open(path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        return data

    def _enlarge_roi(self, pts_clicks, max_width, max_height, board_size=19):
        diff = (abs(pts_clicks[1][0] - pts_clicks[2][0]) + abs(pts_clicks[0][0] - pts_clicks[3][0]))
        added_width_down = int(max_width / board_size / 2)
        added_width_up = int(max_width / board_size / 2) - round(diff / board_size)
        added_height = int(max_height / board_size / 2)
        # added_width_up = 0
        # added_width_down = 0
        # added_height = 0
        pts_clicks[0][1] -= added_height
        pts_clicks[1][1] -= added_height
        pts_clicks[2][1] += added_height
        pts_clicks[3][1] += added_height
        pts_clicks[0][0] -= added_width_up
        pts_clicks[1][0] += added_width_up
        pts_clicks[2][0] += added_width_down
        pts_clicks[3][0] -= added_width_down

        M, max_width, max_height = order_points(np.array(pts_clicks).astype(np.float32))

        return pts_clicks, M, max_width, max_height

    def dump(self, exp_dir):
        with open(os.path.join(exp_dir, 'board_extractor_state.yml'), 'w') as f:
            serialized = dict((key, value) for key, value in self.__dict__.items())
            serialized['M'] = [list(float(f) for f in m) for m in serialized['M']]
            yaml.safe_dump(serialized, f)

    def fit(self, config, cap):

        if config['board_extractor_state'] is not None:
            pts_clicks = self._load_from_state(config['board_extractor_state'])['pts_clicks']
        else:
            clicker = ImageClicker(clicks_num=4)
            pts_clicks = clicker.get_points_of_interest(cap, image_title='Click corners: left upper, right upper, '
                                                                         'right bottom, left bottom')

        _, frame = cap.read()
        M, max_width, max_height = order_points(np.array(pts_clicks).astype(np.float32))

        if self.enlarge:
            pts_clicks, M, max_width, max_height = self._enlarge_roi(pts_clicks,
                                                                     max_width=max_width, max_height=max_height)
        self.M = M
        self.max_width = max_width
        self.max_height = max_height
        self.pts_clicks = [list(p) for p in pts_clicks]

        transformed_frame, _, _ = self.read_board(frame)

        self.width = transformed_frame.shape[0]
        self.height = transformed_frame.shape[1]

        if self.resample:
            x_grid = np.floor(np.linspace(0, 320, config['board_size'])).astype(int)
            y_grid = np.floor(np.linspace(0, 320, config['board_size'])).astype(int)
        else:
            x_grid = np.floor(np.linspace(0, self.width - 1, config['board_size'])).astype(int)
            y_grid = np.floor(np.linspace(0, self.height - 1, config['board_size'])).astype(int)
        self.x_grid = [int(x) for x in x_grid]
        self.y_grid = [int(y) for y in y_grid]

    def read_board(self, frame, debug=False):
        # compute the perspective transform matrix and then apply it
        frame = cv2.warpPerspective(frame, self.M, (self.max_width, self.max_height))
        if self.resample:
            frame = cv2.resize(frame, dsize=(320, 320), interpolation=cv2.INTER_LINEAR)
        return frame, self.x_grid, self.y_grid
