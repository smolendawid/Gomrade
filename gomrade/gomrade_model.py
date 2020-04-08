import abc


class GomradeModel(abc.ABC):
    @abc.abstractmethod
    def fit(self, config, cap):
        pass

    @abc.abstractmethod
    def dump(self, exp_dir):
        pass

    @abc.abstractmethod
    def read_board(self, frame):
        pass
