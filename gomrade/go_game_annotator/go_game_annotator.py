import argparse
import cv2
import tqdm
import yaml
import os
import numpy as np

from gomrade.classifiers.train_validate import collect_examples
from gomrade.classifiers.manual_models import ImageClicker
from gomrade.state_utils import project_stones_state, write_pretty_state
from gomrade.transformations import order_points
from gomrade.images_utils import VideoCaptureFrameMock


def closest(mgx, mgy, point):
    min_i = None
    min = 10000000
    for i, (x, y) in enumerate(zip(mgx.flatten(), mgy.flatten())):
        dist = np.square(point[0] - y) + np.square(point[1] - x)
        if dist < min:
            min_i = i
            min = dist

    return min_i


def _create_annotation(annotation_path, x_grid, y_grid, black_points, white_points, board_size):
    stones_state = ['.'] * (board_size*board_size)
    mgx, mgy = np.meshgrid(x_grid, y_grid)

    for point in black_points:
        i = closest(mgx, mgy, point)
        stones_state[i] = 'B'
    for point in white_points:
        i = closest(mgx, mgy, point)
        stones_state[i] = 'W'

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
    parser.add_argument("--images_path")
    parser.add_argument("--board_size", default=19)
    args = parser.parse_args()

    board_size = args.board_size

    examples = collect_examples(args.images_path)

    x_grid, y_grid, img = None, None, None
    prev_source = ''
    for example, source in tqdm.tqdm(examples):

        annotation_path = example[:-4] + '.txt'
        if os.path.exists(annotation_path):
            print('Annotation for {} exists'.format(example))
            continue

        print('Annotating: {}'.format(example))

        img = cv2.imread(example)
        board_extractor_state_path = os.path.join(source, 'board_extractor_state.yml')

        if source != prev_source:
            x_grid, y_grid, img = _load_params_for_source(img, board_extractor_state_path)

        for x in x_grid:
            for y in y_grid:
                img[x-5:x+5, y-5:y+5, :] = (255, 0, 0)

        img = VideoCaptureFrameMock(img)

        ic = ImageClicker()
        black_points = ic.get_points_of_interest(img, 'click blacks')

        ic = ImageClicker()
        white_points = ic.get_points_of_interest(img, 'click whites')

        _create_annotation(annotation_path, x_grid, y_grid, black_points, white_points, board_size)

        prev_source = source
