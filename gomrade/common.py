import os
import numpy as np

class Move:
    def __init__(self, first_move):
        self._c = first_move

    def switch(self):
        if self._c == 'b':
            self._c = 'w'
        else:
            self._c = 'b'

    @property
    def c(self):
        return self._c

    @c.setter
    def c(self, val):
        self._c = val


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
        files = [os.path.join(d, f) for f in os.listdir(d) if f.endswith('.png') or f.endswith('.jpg') or f.endswith('.JPG')]
        files.sort()

        for f in files:
            all_examples.append(f)
            all_sources.append(d)

    return np.array(all_examples), np.array(all_sources)

