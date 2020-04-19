
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
