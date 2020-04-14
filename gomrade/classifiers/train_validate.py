import argparse
import os

import cv2
import termcolor
import yaml
from sklearn import model_selection
from sklearn.metrics import accuracy_score, f1_score, classification_report
import numpy as np

from gomrade.classifiers.manual_models import ManualBoardStateClassifier, ManualBoardExtractor
from gomrade.state_utils import create_pretty_state
from gomrade.transformations import order_points


def collect_examples(images_path: str) -> [[]]:
    """
    :param images_path: Path to data main directory. Should have 2 dir levels - each game
    should have images in its own dir
    :return: filename, source name, list with board points
    """
    all_examples = []
    all_sources = []

    dirs = [os.path.join(images_path, d) for d in os.listdir(images_path)
            if os.path.isdir(os.path.join(images_path, d))]

    for d in dirs:
        files = [os.path.join(d, f) for f in os.listdir(d) if f.endswith('.png') or f.endswith('.jpg')]

        for f in files:
            all_examples.append(f)
            all_sources.append(d)

    return np.array(all_examples), np.array(all_sources)


def load_board_extractor_state(source):
    with open(os.path.join(source, 'board_extractor_state.yml')) as f:
        clicks = yaml.load(f)['pts_clicks']

    return np.array(clicks)


def load_board_state_classifier_state(source):
    with open(os.path.join(source, 'board_state_classifier_state.yml')) as f:
        data = yaml.load(f)

    return data['black_colors'], data['white_color'], data['board_colors'], data['x_grid'], data['y_grid']


def run_fold(train, valid):
    predictions = []
    references = []
    for ex in valid:
        image = cv2.imread(ex[0])
        with open(ex[0][:-4] + '.txt') as f:
            reference = f.read().replace('\n', '').replace(' ', '')
        pts_clicks = load_board_extractor_state(ex[1])

        M, max_width, max_height = order_points(np.array(pts_clicks).astype(np.float32))
        image = cv2.warpPerspective(image, M, (max_width, max_height))

        mbc = ManualBoardStateClassifier(width=None, height=None)
        config = {'board_state_classifier_state': os.path.join(ex[1], 'board_state_classifier_state.yml')}
        mbc.fit(config=config, cap=None)
        stones_state, _ = mbc.read_board(image)
        stones_state = "".join(stones_state)

        predictions.append(stones_state)
        references.append(reference)

    return np.array(references), np.array(predictions)


def error_analysis(ref, pred, valid):
    for ref, pred, v in zip(ref, pred, valid):
        if ref != pred:
            ref_lines = create_pretty_state(ref).splitlines()
            pred_lines = create_pretty_state(pred).splitlines()

            print(v[0])
            for ref_line, pred_line in zip(ref_lines, pred_lines):
                pred_line_clolored = ''.join(termcolor.colored(j, 'red') if i!=j else j for i, j in zip(ref_line, pred_line))

                new_line = ref_line + '\t' + pred_line_clolored
                print(new_line)


def stones_state_to_int(stones_state):
    mapping = {'.': 0, 'B': 1, 'W': 2}
    return [mapping[i] for i in list("".join(stones_state))]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--images_path", help='Should have 2 dir levels - each game should have images in its own dir')
    args = parser.parse_args()

    images_path = args.images_path

    examples, sources = collect_examples(args.images_path)
    examples = np.array([[e, s] for e, s in zip(examples, sources)])

    cv = model_selection.LeaveOneGroupOut()

    f1s_refs = []
    f1s_preds = []
    all_elements = 0
    the_same = 0
    all_ex = 0
    full_sources_correct = 0
    sources_num = 0
    for train_ind, valid_ind in cv.split(examples, groups=sources):

        train = examples[train_ind]
        valid = examples[valid_ind]
        print('\n\nSource: {}, num of valid examples: {}'.format(valid[0][1], len(valid)))

        ref, pred = run_fold(train, valid)

        ref_ind = stones_state_to_int(ref)
        pred_ind = stones_state_to_int(pred)

        # Metrics
        the_same += sum(r == p for r, p in zip(ref, pred))
        all_ex += len(ref)

        acc = sum(r == p for r, p in zip(ref, pred))/len(ref)
        if acc == 100:
            full_sources_correct += 1
        sources_num += 1

        f1s_refs.extend(ref_ind)
        f1s_preds.extend(pred_ind)

        print("Accuracy: {}".format(acc))
        print(classification_report(ref_ind, pred_ind))

        error_analysis(ref, pred, valid)

    print("All images to classify: {}".format(all_ex))
    print("All sources correct: {}".format(full_sources_correct/sources_num))
    print("Accuracy: {}".format(the_same/all_ex))
    print(classification_report(f1s_refs, f1s_preds))
