import os
import cv2
import time

from gomrade.classifiers.keras_model import KerasModel, crop_stone
from gomrade.classifiers.manual_models import ManualBoardExtractor, ManualBoardStateClassifier
from gomrade.images_utils import VideoCaptureFrameMock


if __name__ == '__main__':

    data_path = '../data/sample_data/'
    examples = []
    for root, dirs, files in os.walk(data_path, topdown=False):
        for name in files:
            if name.endswith('.jpg'):
                examples.append(os.path.join(root, name))

    cl1 = KerasModel('/Users/dasm/projects/Gomrade/data/go_model.h5')
    cl2 = ManualBoardStateClassifier()
    mbe1 = ManualBoardExtractor(resample=True, enlarge=True)
    mbe2 = ManualBoardExtractor(resample=False, enlarge=False)

    for exmple in examples:
        direct = '/'.join(exmple.split('/')[:-1])
        image = cv2.imread(exmple)
        with open(exmple[:-4] + '.txt') as f:
            reference = f.read().replace('\n', '').replace(' ', '')

        config = {
            'board_extractor_state': os.path.join(direct, 'board_extractor_state.yml'),
            'board_state_classifier_state': os.path.join(direct, 'board_state_classifier_state.yml'),
            'board_size': 19,
        }
        cap = VideoCaptureFrameMock(image)
        _, frame = cap.read()

        cl1.fit(config=config, cap=cap)
        cl2.fit(config=config, cap=cap)

        # ====================================
        start = time.time()
        mbe1.fit(config=config, cap=cap)
        print(f'board extractor fit False False {time.time() - start}')

        # ====================================
        start = time.time()
        frame, x_grid, y_grid = mbe1.read_board(frame, debug=False)
        print(f'board extractor False False {time.time() - start}')

        # ====================================
        start = time.time()
        stones_state, frame = cl1.read_board(frame, x_grid, y_grid, debug=False)
        print(f'keras {time.time() - start}')

        # ====================================
        frame_for_crop = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        start = time.time()
        for x in x_grid:
            for y in y_grid:
                cropped = crop_stone(frame_for_crop, x, y, x_margin=16, y_margin=16)
                cropped = cropped.reshape(-1).reshape(1, 32, 32, 1)/256
        print(f'crop stone mock {time.time() - start}')

        # ====================================
        start = time.time()
        mbe2.fit(config=config, cap=cap)
        print(f'board extractor fit {time.time() - start}')

        # ====================================
        start = time.time()
        frame, x_grid, y_grid = mbe2.read_board(frame, debug=False)
        print(f'board extractor {time.time() - start}')

        # ====================================
        start = time.time()
        stones_state, frame = cl2.read_board(frame, x_grid, y_grid, debug=False)
        print(f'board state {time.time() - start}')

        stones_state = "".join(stones_state)

        # ====================================
        start = time.time()
        for i in x_grid:
            for j in y_grid:
                area = cl2._get_pt_area(frame, i, j)
        print(f'get pt area mock {time.time() - start}')

        print(f'\n')

