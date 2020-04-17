from sgfmill import sgf, ascii_boards, boards
from collections import Counter

from gomrade.state_utils import project_stones_state
from gomrade.state_utils import create_pretty_state


"""
What can happen:

# Casual game:

1. Color plays normally:
- One extra stone for color and the same num of the other color

2. Color plays and kills:
- One extra stone for color and at least one less of the other color

3. Undo to some move of a player
- Check previous states and if it was, generate

5. Undo to some move of AI
- Check previous states and if it was, wait

5. Undo to other move of a player
- Check previous states and whether they differ with just one stone of player color

6. Undo to other move of which is a kill
- Pff

# Introductions:

1. Game state is introduced without sgf

2. Game state is loaded from sgf

3. Game state is strongly changed but some history is preserved


# Errors:

1. Random stone is switched to opposite
- Just accept, fill with pass

2. Stone or stones disappear

3. A few stones are introduced



1. Easy-peasy
2. Need to check if it was a kill or a mistake. How verify the kill?
- maybe checking the liberties will be necessary?
3. 


"""

from enum import Enum

_W = 'W'
_B = 'B'
_E = '.'


class Task(Enum):
    REGULAR = 0
    KILL = 1
    UNDO = 2


class GameTracker:
    def __init__(self):
        self.game = None
        self.board_size = None
        self.komi = None
        self.state_history = None
        self._task = None

    @property
    def task(self):
        return self._task

    def _has_only_one_color(self, blacks, whites):
        has_only_one_color = False
        if (whites == 0 and blacks > 0) or (blacks == 0 and whites > 0):
            has_only_one_color = True
        return has_only_one_color

    def _has_empty(self, empties):
        has_empty = False
        if empties > 0:
            has_empty = True
        return has_empty

    def _is_kill(self, diff):
        counter = Counter(diff)
        blacks = counter[_B]
        whites = counter[_W]
        empties = counter[_E]

        is_kill = False
        if self._has_only_one_color(blacks, whites) and self._has_empty(empties):
            is_kill = True
        return is_kill

    def _is_undo(self, stones_state):
        is_undo = False
        for prev in self.state_history:
            if stones_state == prev:
                is_undo = True
        return is_undo

    def _diff(self, stones_state):
        prev_state = self.state_history[-1]
        diff = "".join([s for s, p in zip(stones_state, prev_state) if s != p])

        return diff

    def load_game(self, path):
        with open(path, 'r') as f:
            game_str = f.read()
        self.game = sgf.Sgf_game.from_string(game_str)

    def save_game(self, path):
        with open(path, 'w') as f:
            f.write(self.to_string())

    def to_string(self):
        return self.game.serialise().decode("utf-8")

    def create_empty(self, size, komi):
        self.game = sgf.Sgf_game(size=size, encoding="UTF-8")
        self.board_size = size
        self.komi = komi
        self.state_history = ['.' * size * size]
        root_node = self.game.get_root()
        root_node.set("KM", komi)

    def vanilla_parse(self, stones_state):
        """Temporary method """
        # tmp = ''
        self.create_empty(self.board_size, self.komi)

        for row in range(self.board_size):
            for col in range(self.board_size):
                c = stones_state[row*self.board_size + col]
                if c == '.':
                    continue
                node = self.game.extend_main_sequence()
                node.set_move(c.lower(), (row, col))

    def replay_position(self, stones_state):

        stones_state = project_stones_state(stones_state, flip=True, rotate=False)

        if self._is_undo(stones_state):
            self._task = Task.UNDO
        else:
            diff = self._diff(stones_state)

            if diff == _W or diff == _B:
                self._task = Task.REGULAR
            if self._is_kill(diff):
                self._task = Task.KILL
            if stones_state in self.state_history:
                self._task = Task.UNDO

        # node = self.game.extend_main_sequence()
        # node.set_move('b', (2, 3))

        self.state_history.append(stones_state)


if __name__ == '__main__':

    gt = GameTracker()
    gt.create_empty(size=19, komi=6.5)

    stones_state = list('....................' * 19)

    stones_state[60] = 'B'
    print(create_pretty_state(stones_state) + '\n\n')
    gt.replay_position(stones_state)
