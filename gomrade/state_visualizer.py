import cv2


class StateVisualizer:
    def __init__(self):
        pass

    def show_cam(self, frame):
        res = cv2.flip(frame, -1)
        cv2.imshow('frame', res)

    def plot_board(self, frame):
        raise NotImplementedError
