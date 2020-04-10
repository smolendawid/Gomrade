from sgfmill import sgf


class GameTracker:
    def __init__(self, tmp_path):
        self.tmp_path = tmp_path

    def many_stones_added(self):
        pass

    def wrong_color_added(self):
        pass

    def seems_like_undo(self):
        pass

    def seems_like_reset(self):
        pass

    def translate_stones_state(self):
        pass

    def update_sgf(self):
        pass

    def to_string(self):
        pass

    def replay_position(self, stones_state):
        with open(self.tmp_path, 'r') as f:
            game_str = f.read()
        game = sgf.Sgf_game.from_string(game_str)
        root_node = game.get_root()
        a = [node.get_move() for node in game.get_main_sequence()]

        for i in stones_state:
            pass

        self.update_sgf()

        with open(self.tmp_path, "w") as f:
            f.write(self.to_string(game))


if __name__ == '__main__':
    gt = GameTracker('/Users/dasm/Downloads/Xie_Yimin-Fujisawa_Rina.sgf')
    gt.replay_position(stones_state='....................'*19)
