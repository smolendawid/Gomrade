
from subprocess import Popen, PIPE

from gtp.gtp import parse_vertex, gtp_move, gtp_color
from gtp.gtp import BLACK, WHITE, PASS


class GTPSubProcess(object):

    def __init__(self, label, args):
        self.label = label
        self.subprocess = Popen(args, stdin=PIPE, stdout=PIPE, encoding='utf8')
        print("{} subprocess created".format(label))

    def send(self, data):
        print("sending {}: {}".format(self.label, data))
        self.subprocess.stdin.write(data)
        self.subprocess.stdin.flush()
        result = ""

        while True:
            data = self.subprocess.stdout.readline()
            if not data.strip():
                break
            result += data
        print("got: {}".format(result))
        return result

    def close(self):
        print("quitting {} subprocess".format(self.label))
        self.subprocess.communicate("quit\n")


class GTPFacade(object):

    def __init__(self, label, args):
        self.label = label
        self.gtp_subprocess = GTPSubProcess(label, args)

    def name(self):
        self.gtp_subprocess.send("name\n")

    def version(self):
        self.gtp_subprocess.send("version\n")

    def boardsize(self, boardsize):
        self.gtp_subprocess.send("boardsize {}\n".format(boardsize))

    def komi(self, komi):
        self.gtp_subprocess.send("komi {}\n".format(komi))

    def clear_board(self):
        self.gtp_subprocess.send("clear_board\n")

    def genmove(self, color):
        message = self.gtp_subprocess.send(
            "genmove {}\n".format(gtp_color(color)))
        assert message[0] == "="
        return parse_vertex(message[1:].strip())

    def showboard(self):
        self.gtp_subprocess.send("showboard\n")

    def play(self, color, vertex):
        self.gtp_subprocess.send("play {}\n".format(gtp_move(color, vertex)))

    def final_score(self):
        self.gtp_subprocess.send("final_score\n")

    def load_sgf(self, path):
        self.gtp_subprocess.send("loadsgf {}\n".format(path))

    def close(self):
        self.gtp_subprocess.close()
