import argparse
import os
import yaml
from sklearn import model_selection
from sklearn.metrics import accuracy_score, f1_score
import numpy as np

def collect_examples(images_path: str) -> [[]]:
    """
    :param images_path: Path to data main directory. Should have 2 dir levels - each game
    should have images in its own dir
    :return: filename, source name, list with board points
    """
    all_examples = []

    dirs = [os.path.join(images_path, d) for d in os.listdir(images_path)
            if os.path.isdir(os.path.join(images_path, d))]

    for d in dirs:
        files = [os.path.join(d, f) for f in os.listdir(d) if f.endswith('.png') or f.endswith('.jpg')]

        for f in files:
            all_examples.append([f, d])

    return np.array(all_examples)


def load_board_extractor_state(dirs):
    pts_clicks = []
    for d in dirs:
        with open(os.path.join(d, 'board_extractor_state.yml')) as f:
            clicks = yaml.load(f)['pts_clicks']
        pts_clicks.append(clicks)

    return np.array(pts_clicks)


def train_validate(train, valid):
    for ex in train:
        pass

    return None, None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--images_path", help='Should have 2 dir levels - each game should have images in its own dir')
    args = parser.parse_args()

    images_path = args.images_path

    all_examples = collect_examples(images_path)
    pts_clicks = load_board_extractor_state(all_examples[:, 1])

    all_examples = np.hstack((all_examples, pts_clicks))

    cv = model_selection.KFold(n_splits=5)
    # cv = model_selection.GroupKFold(n_splits=5)

    metrics = []
    for train_ind, valid_ind in cv.split(all_examples):
        train = all_examples[train_ind]
        valid = all_examples[valid_ind]

        ref, pred = train_validate(train, valid)

        f1 = f1_score(ref, pred)
        acc = accuracy_score(ref, pred)
        metrics.append([f1, acc])
