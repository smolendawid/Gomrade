import argparse
import os
import numpy as np

import cv2
import tqdm
import yaml

from gomrade.classifiers.validate_full_images import collect_examples
from gomrade.classifiers.manual_models import ManualBoardExtractor
from gomrade.images_utils import VideoCaptureFrameMock
from gomrade.transformations import order_points
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def load_params(img, board_extractor_state_path, board_size):

    with open(board_extractor_state_path) as f:
        pts_clicks = yaml.load(f)['pts_clicks']

    M, max_width, max_height = order_points(np.array(pts_clicks).astype(np.float32))

    diff = (abs(pts_clicks[1][0] - pts_clicks[2][0]) + abs(pts_clicks[0][0] - pts_clicks[3][0]))
    added_width_down = int(max_width/board_size/2)
    added_width_up = int(max_width/board_size/2) - round(diff/board_size)
    added_height = int(max_height/board_size/2)
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

    img_transformed = cv2.warpPerspective(img, M, (max_width, max_height))
    img_transformed = cv2.resize(img_transformed, dsize=(max_width, max_width))

    width = img_transformed.shape[0]
    height = img_transformed.shape[1]

    x_grid = np.floor(np.linspace(added_width_up*2, width - 1-added_width_up*2, board_size)).astype(int)
    y_grid = np.floor(np.linspace(added_height, height - 1-added_height, board_size)).astype(int)
    x_grid = [int(x) for x in x_grid]
    y_grid = [int(y) for y in y_grid]

    # img = cv2.warpPerspective(img, M, (max_width, max_height))

    return x_grid, y_grid, img_transformed


def crop_stone(image, x, y, x_margin=33, y_margin=33):
    mask = np.zeros((x_margin*2, y_margin*2, 3))
    mask_x_start = 0
    mask_y_start = 0
    mask_x_stop = image.shape[0]
    mask_y_stop = image.shape[1]

    x_start = x - x_margin
    x_stop = x + x_margin
    y_start = y - y_margin
    y_stop = y + y_margin
    if x-x_margin < 0:
        mask_x_start = abs(x - x_margin)
        x_start = 0
    elif x+x_margin > image.shape[0]:
        mask_x_start = x_margin*2 - (image.shape[1] - abs(x - x_margin))
        x_stop = image.shape[0]

    if y-y_margin < 0:
        mask_y_start = abs(y - y_margin)
        y_start = 0
    elif y+y_margin > image.shape[1]:
        mask_y_start = y_margin*2 - (image.shape[1] - abs(y - y_margin))
        y_stop = image.shape[1]

    mask[mask_x_start:mask_x_stop, mask_y_start:mask_y_stop, :] = image[x_start:x_stop, y_start:y_stop, :]
    return mask


def rewrite_labels_to_annot(dataset_path, yolo_path, plot=False):
    board_size = 19

    examples, sources = collect_examples(dataset_path)

    prev_source = ''
    empty_position_counter = 0

    for example, source in tqdm.tqdm(zip(examples, sources)):
        source_name = source.split('/')[-1]
        example_name = example.split('/')[-1]

        os.makedirs(os.path.join(yolo_path), exist_ok=True)
        os.makedirs(os.path.join(yolo_path, source_name), exist_ok=True)

        annotation_path = example[:-4] + '.txt'
        with open(annotation_path) as f:
            annotation = f.read().replace(' ', '').replace('\n', '')

        img = cv2.imread(example)
        cap = VideoCaptureFrameMock(img)

        if source != prev_source:
            board_extractor_state_path = os.path.join(source, 'board_extractor_state.yml')
            config = {
                'board_extractor_state': board_extractor_state_path,
                'board_size': board_size
            }

            mbe = ManualBoardExtractor(resample=True, enlarge=False)
            mbe.fit(config=config, cap=cap)
            mbe.resample = True

        img, x_grid, y_grid = mbe.read_board(img)

        stone_w = (x_grid[1] - x_grid[0])
        stone_h = stone_w

        if plot:
            fig, ax = plt.subplots(1)
            for row, y in enumerate(x_grid):
                for col, x in enumerate(y_grid):
                    img[y-1:y+1, x-1:x+1, :] = (255, 0, 0)
                    if annotation[col*board_size + row] == 'W' or annotation[col*board_size + row] == 'B':
                        rect = patches.Rectangle((x-stone_w/2, y-stone_h*1.1/2), stone_w, stone_h, linewidth=1,
                                                 edgecolor='r', facecolor='none')
                        ax.add_patch(rect)
            ax.imshow(img)

            plt.show(block=False)
        i = 0
        for row, x in enumerate(x_grid):
            for col, y in enumerate(y_grid):
                name_ann = os.path.join(yolo_path, source_name, f'{example_name[:-4]}_{i}.txt')
                name_img = os.path.join(yolo_path, source_name, f'{example_name[:-4]}_{i}.jpg')

                # save image
                cropped = crop_stone(img, x, y)
                if cropped.shape[0] > 0 and cropped.shape[1] > 0 :
                    cv2.imwrite(name_img, cropped)
                else:
                    raise ValueError()

                # save label
                with open(name_ann, 'w') as f:
                    cl = annotation[row*board_size + col]
                    if cl == '.':
                        empty_position_counter += 1
                        f.write("{}\n".format(0))
                    if cl == 'B':
                        f.write("{}\n".format(1))
                    if cl == 'W':
                        f.write("{}\n".format(2))
                i += 1


def create_split(yolo_path):
    examples, sources = collect_examples(yolo_path)

    with open(os.path.join(yolo_path, 'train.txt'), 'w') as f_train:
        with open(os.path.join(yolo_path, 'valid.txt'), 'w') as f_valid:
            for example in examples:
                if '20_03_29_16_33_37' in example:
                    f_valid.write(example + '\n')
                else:
                    f_train.write(example + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--images_path")
    parser.add_argument("--yolo_path")
    args = parser.parse_args()

    rewrite_labels_to_annot(args.images_path, args.yolo_path, plot=False)
    create_split(args.yolo_path)
