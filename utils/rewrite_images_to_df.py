import argparse
import os
import numpy as np

import cv2
import tqdm
import pandas as pd

from gomrade.common import collect_examples
from gomrade.classifiers.manual_models import ManualBoardExtractor
from gomrade.images_utils import VideoCaptureFrameMock
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class_mapping = {
    '.': 0,
    'B': 1,
    'W': 2,
}
X_MARGIN = 16
Y_MARGIN = 16


def crop_stone(image, x, y, x_margin=16, y_margin=16):
    mask = np.zeros((x_margin*2, y_margin*2))
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

    mask[mask_x_start:mask_x_stop, mask_y_start:mask_y_stop] = image[x_start:x_stop, y_start:y_stop]
    return mask


def write_to_imgs(target_root, source_name, example_name, img, annotation, row, col, board_size):
    name_ann = os.path.join(target_root, source_name, f'{example_name[:-4]}_{i}.txt')
    name_img = os.path.join(target_root, source_name, f'{example_name[:-4]}_{i}.jpg')

    # save image
    cropped = crop_stone(img, x, y)
    if cropped.shape[0] > 0 and cropped.shape[1] > 0:
        cv2.imwrite(name_img, cropped)
    else:
        raise ValueError()

    # save label
    with open(name_ann, 'w') as f:
        cl = annotation[row * board_size + col]
        if cl == '.':
            f.write("{}\n".format(0))
        if cl == 'B':
            f.write("{}\n".format(1))
        if cl == 'W':
            f.write("{}\n".format(2))


def rewrite_labels_to_annot(dataset_path, target_root, plot=False):
    board_size = 19

    examples, sources = collect_examples(dataset_path)

    prev_source = ''
    empty_position_counter = 0
    labels = []
    images_inds = []
    example_names = []
    sources_str = []
    images_flat = []

    for example, source in tqdm.tqdm(zip(examples, sources)):
        source_name = source.split('/')[-1]
        example_name = example.split('/')[-1]

        os.makedirs(os.path.join(target_root), exist_ok=True)
        os.makedirs(os.path.join(target_root, source_name), exist_ok=True)

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
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        stone_w = (x_grid[1] - x_grid[0])
        stone_h = stone_w

        if plot:
            fig, ax = plt.subplots(1)
            for row, y in enumerate(x_grid):
                for col, x in enumerate(y_grid):
                    img[y-1:y+1, x-1:x+1] = 0
                    if annotation[col*board_size + row] == 'W' or annotation[col*board_size + row] == 'B':
                        rect = patches.Rectangle((x-stone_w/2, y-stone_h*1.1/2), stone_w, stone_h, linewidth=1,
                                                 edgecolor='r', facecolor='none')
                        ax.add_patch(rect)
            ax.imshow(img)

            plt.show(block=False)
        i = 0
        for row, x in enumerate(x_grid):
            for col, y in enumerate(y_grid):
                # write_to_imgs(target_root, source_name, example_name, img, annotation, row, col, board_size)
                #
                # name_ann = os.path.join(target_root, source_name, f'{example_name[:-4]}_{i}.txt')
                # name_img = os.path.join(target_root, source_name, f'{example_name[:-4]}_{i}.jpg')

                # save image
                cropped = crop_stone(img, x, y, x_margin=X_MARGIN, y_margin=Y_MARGIN)
                assert cropped.shape[0] > 0 and cropped.shape[1] > 0, "cropping failed"

                cl = class_mapping[annotation[row * board_size + col]]
                cropped_flat = cropped.reshape(-1).astype(np.uint8)

                images_flat.append(cropped_flat)
                labels.append(cl)
                images_inds.append(i)
                sources_str.append(source_name)

                i += 1

    print('saving...')
    columns = [str(i) for i in range(X_MARGIN*Y_MARGIN*2*2)]
    df = pd.DataFrame(images_flat, columns=columns)
    df['label'] = labels
    df['image_ind'] = images_inds
    df['source'] = sources_str
    df.to_csv('data.csv')

    data = pd.read_csv('data.csv')
    imgs = data[[str(i) for i in range(X_MARGIN*Y_MARGIN*2*2)]].values
    plt.imshow(imgs[150].reshape(X_MARGIN*2,Y_MARGIN*2))
    plt.show()


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
    parser.add_argument("--target_root")
    args = parser.parse_args()

    rewrite_labels_to_annot(args.images_path, args.target_root, plot=False)
    # create_split(args.target_root)
