import os

from sgfmill import sgf, ascii_boards, boards
from sgfmill.sgf import Tree_node

from collections import Counter

from gomrade.state_utils import project_stones_state
from gomrade.state_utils import create_pretty_state
from gomrade.common import Move

from enum import Enum


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


def index2pos(ind, board_size):
    row = ind // board_size
    column = ind % board_size
    return row, column


_W = 'W'
_B = 'B'
_E = '.'


class Task(Enum):
    NOT_SET = 0
    REGULAR = 1
    KILL = 2
    UNDO = 3
    MANY_ADDED = 4
    DISAPPEAR = 5
    OTHER_ERROR = 6
    FIRST_POSITION = 7


class SgfTranslator:
    def __init__(self, board_size: int, komi: float, root_path: str):
        """ Translate the recognized stones and recognized move character, employing the history of the game, to
        SGF file. If it's unable to track the game, it save the current state as game{i}.sgf and creates new game from
        the state.
        """
        self.game = None
        self.board_size = board_size
        self.komi = komi

        self.mr = MoveRecognizer(size=board_size)
        self.interpreted_action = []
        self.curr_node = None
        self.nodes_history = []

        self.sgf_ind = 0
        self.root_path = root_path
        self.path = os.path.join(self.root_path, 'game.sgf')
        self.create_empty()

    def load_game(self, path):
        with open(path, 'r') as f:
            game_str = f.read()
        self.game = sgf.Sgf_game.from_string(game_str)

    def save_game(self, path):
        with open(path, 'w') as f:
            f.write(self.to_string())

    def to_string(self):
        return self.game.serialise().decode("utf-8")

    def create_empty(self, played='w'):
        self.game = sgf.Sgf_game(size=self.board_size, encoding="UTF-8")

        self.game.set_date()
        root_node = self.game.get_root()
        root_node.set("KM", self.komi)
        self.curr_node = self.game.get_root()

    def _setup_state(self, stones_state):
        """ Setup board when state is not understood with AW AB AE """
        blacks = []
        whites = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                c = stones_state[row*self.board_size + self.board_size - col - 1]
                if c == '.':
                    continue
                elif c == 'B':
                    blacks.append((row, col))
                elif c == 'W':
                    whites.append((row, col))
        self.curr_node.set_setup_stones(black=blacks, white=whites)

    def parse(self, stones_state):
        c, move = self.mr.replay_position(stones_state)

        if self.mr.task == Task.FIRST_POSITION:
            if not all([s == '.' for s in stones_state]):
                self.create_empty()
                self._setup_state(stones_state)
                self.save_game(self.path)

            return self.mr.task
        elif self.mr.task == Task.REGULAR or self.mr.task == Task.KILL:
            self.curr_node = self.curr_node.new_child()
            self.curr_node.set_move(c, move)
            self.save_game(self.path)

        elif self.mr.task == Task.UNDO:
            # self.curr_node.reparent()
            if len(self.nodes_history) > 0:
                self.curr_node = self.nodes_history[self.mr.last_undo_ind - 1]
                # self.curr_node = self.game.get_main_sequence()[self.gt.last_undo_ind]
        else:
            self.sgf_ind += 1
            self.save_game(os.path.join(self.root_path, 'game{}.sgf'.format(self.sgf_ind)))
            self.create_empty()
            self._setup_state(stones_state)
            self.save_game(self.path)

        self.nodes_history.append(self.curr_node)
        return self.mr.task


class MoveRecognizer:
    def __init__(self, size: int, playing='b'):
        """
        Interpret the status of the game, e.g. the character of the move.
        Moves that can be recognized are:
        - regular move
        - kill move
        - undo move
        - undo move
        - many stones added
        - stones disappeared
        - other non typical action
        """
        self.raw_state_history = None
        self._task = None
        self.color_to_play = Move(first_move=playing)
        self.size = size
        self.raw_state_history = []

        self.last_undo_ind = None

    @property
    def task(self):
        return self._task

    def _has_only_one_color(self, blacks, whites):
        has_only_one_color = False
        if (whites == 0 and blacks > 0) or (blacks == 0 and whites > 0):
            has_only_one_color = True
        return has_only_one_color

    def _removed_only_one_color(self, diff_prev):
        removed_only_one_color = False
        counter = Counter(diff_prev)
        whites = counter[_W]
        blacks = counter[_B]

        if (whites == 0 and blacks > 0) or (blacks == 0 and whites > 0):
            removed_only_one_color = True
        return removed_only_one_color

    def _has_empty(self, empties):
        has_empty = False
        if empties > 0:
            has_empty = True
        return has_empty

    def _is_kill(self, counter, diff_prev):
        is_kill = False
        if self._has_only_one_color(counter[_B], counter[_W]) and self._has_empty(counter[_E]):
            # only one color should be removed
            counter_prev = Counter(diff_prev)
            if (counter[_B] > 0 and counter_prev[_W] > 0) or (counter[_W] > 0 and counter_prev[_B] > 0):
                is_kill = True
        return is_kill

    def _get_kill_ind(self, counter, diff_new, diff_inds):
        kill_ind = None
        for c, i in zip(diff_new, diff_inds):
            if counter[_B] > 0:
                if c == _B:
                    kill_ind = i
                    break
            elif counter[_W] > 0:
                if c == _W:
                    kill_ind = i
                    break
        return kill_ind

    def _is_undo(self, stones_state):
        is_undo = False
        color = None
        undo_ind = None
        for i, (prev, c) in enumerate(self.raw_state_history):
            if stones_state == prev:
                color = c
                undo_ind = i
                is_undo = True
                break

        return is_undo, color, undo_ind

    def _disappears(self, counter):

        disappears = False
        if self._has_empty(counter[_E]) and counter[_B] == 0 and counter[_W] == 0:
            disappears = True
        return disappears

    def _many_added(self, counter):

        many_added = False
        if not self._has_empty(counter[_E]) and ((counter[_B] > 0 and counter[_W] > 0)
                                                 or counter[_W] > 1 or counter[_B] > 1):
            many_added = True
        return many_added

    def _diff(self, stones_state):
        """
        :return: stones that appeared, stones that are replaced, indices of changes
        """
        prev_state, _ = self.raw_state_history[-1]
        diff = [(s, p, i) for i, (s, p) in enumerate(zip(stones_state, prev_state)) if s != p]

        diff_new, diff_prev, diff_inds = list(list(zip(*diff)))

        return diff_new, diff_prev, diff_inds

    def _understand_task(self, stones_state):

        self._task = Task.NOT_SET
        move = None

        if len(self.raw_state_history) == 0:
            self._task = Task.FIRST_POSITION
            return move

        is_undo, color, undo_ind = self._is_undo(stones_state)
        if is_undo:
            self.last_undo_ind = undo_ind
            self._task = Task.UNDO
            self.color_to_play.c = color
        else:
            diff_new, diff_prev, diff_inds = self._diff(stones_state)

            if len(diff_new) == 1 and (diff_new[0][0] == _W or diff_new[0][0] == _B):
                self._task = Task.REGULAR
                move = index2pos(diff_inds[0], self.size)
            else:
                counter = Counter(diff_new)

                if self._is_kill(counter, diff_prev):
                    self._task = Task.KILL
                    kill_ind = self._get_kill_ind(counter, diff_new, diff_inds)
                    move = index2pos(kill_ind, self.size)
                elif self._disappears(counter):
                    self._task = Task.DISAPPEAR
                elif self._many_added(counter):
                    self._task = Task.MANY_ADDED
                else:
                    self._task = Task.OTHER_ERROR
                    # self._find_closest_history()

        # node = self.game.extend_main_sequence()
        # node.set_move('b', (2, 3))
        return move

    def replay_position(self, stones_state):

        stones_state = project_stones_state(stones_state, flip=True, rotate=False)

        move = self._understand_task(stones_state)
        curr_color = self.color_to_play.c

        # if it's a first move
        if self.task != Task.UNDO and self.task != Task.FIRST_POSITION:
            self.color_to_play.switch()
        self.raw_state_history.append((stones_state, curr_color))

        return curr_color, move


if __name__ == '__main__':

    gt = MoveRecognizer(size=19)

    stones_state = list('....................' * 19)

    stones_state[60] = 'B'
    print(create_pretty_state(stones_state) + '\n\n')
    gt.replay_position(stones_state)
