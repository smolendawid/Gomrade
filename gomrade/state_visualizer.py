import cv2


class StateVisualizer:
    def __init__(self):
        pass

    def show_cam(self, frame):
        res = cv2.flip(frame, -1)
        cv2.imshow('frame', res)
        cv2.waitKey(1)

    def plot_board(self, frame):
        raise NotImplementedError


def show_board_with_grid(frame, x_grid, y_grid, m=3):
    for i in x_grid:
        for j in y_grid:
            frame[i-m:i+m, j-m:j+m] = (0, 0, 0)
    cv2.imshow('example board [click to continue]', frame)
    cv2.waitKey(1)
