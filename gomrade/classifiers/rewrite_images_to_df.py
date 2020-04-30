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
from gomrade.classifiers.keras_model import crop_stone, class_mapping

X_MARGIN = 16
Y_MARGIN = 16


def rewrite_labels_to_annot(dataset_path, target_root, plot=False):
    board_size = 19

    examples, sources = collect_examples(dataset_path)

    prev_source = ''

    labels = []
    images_inds = []
    example_names = []
    sources_str = []
    images_flat = []
    os.makedirs(os.path.join(target_root), exist_ok=True)

    for example, source in tqdm.tqdm(zip(examples, sources)):
        source_name = source.split('/')[-1]
        example_name = example.split('/')[-1]

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

            mbe = ManualBoardExtractor(resample=True, enlarge=True)
            mbe.fit(config=config, cap=cap)
            mbe.resample = True

            img, x_grid, y_grid = mbe.read_board(img)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            stone_w = (x_grid[1] - x_grid[0])
            stone_h = stone_w

            if plot:
                fig, ax = plt.subplots(1)
                for row, x in enumerate(x_grid):
                    for col, y in enumerate(y_grid):
                        img[x-1:x+1, y-1:y+1] = 0
                        if annotation[col*board_size + row] == 'W' or annotation[col*board_size + row] == 'B':
                            rect = patches.Rectangle((x-stone_w/2, y-stone_h*1.1/2), stone_w, stone_h, linewidth=1,
                                                     edgecolor='r', facecolor='none')
                            ax.add_patch(rect)
                ax.imshow(img)

                plt.show(block=False)
            i = 0
            for row, x in enumerate(x_grid):
                for col, y in enumerate(y_grid):
                    cropped = crop_stone(img, x, y, x_margin=X_MARGIN, y_margin=Y_MARGIN)
                    assert cropped.shape[0] > 0 and cropped.shape[1] > 0, "cropping failed"

                    cl = class_mapping[annotation[row * board_size + col]]
                    cropped_flat = cropped.reshape(-1).astype(np.uint8)
                    images_flat.append(cropped_flat)
                    labels.append(cl)
                    images_inds.append(i)
                    sources_str.append(source_name)
                    example_names.append(example_name)

                    i += 1
        prev_source = source

    print('saving...')
    columns_img = [str(i) for i in range(X_MARGIN*2*Y_MARGIN*2)]
    columns_rest = ['label', 'image_ind', 'example', 'source',]
    df = pd.DataFrame(images_flat, columns=columns_img)
    df['label'] = labels
    df['image_ind'] = images_inds
    df['example'] = example_names
    df['source'] = sources_str
    df.to_csv(os.path.join(target_root, 'data.csv'))

    data = pd.read_csv(os.path.join(target_root, 'data.csv'))
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

    rewrite_labels_to_annot(args.images_path, args.target_root, plot=True)
    # create_split(args.target_root)
