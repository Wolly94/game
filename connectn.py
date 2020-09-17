from abstract_classes import BoardState, PlayerIndex
from helper import IndexAction

def_rows = 6
def_cols = 7
def_n = 4
neutral = -1

class ConnectNState(BoardState):
    def __init__(self, rows = def_rows, cols = def_cols, connect = def_n, board = None):
        self.cols = cols
        self.rows = rows
        self.board = board # board[0][0] is bottom left
        self.connect = connect
        if self.board is None:
            self.reset()

    def reset(self):
        # self.board[i][j] is i-th row and j-th column
        self.board = [[neutral for _ in range(self.cols)] for _ in range(self.rows)]

    def get_actions(self, pp):
        r = []
        for j in range(self.cols):
            for i in range(self.rows):
                if self.board[i][j] == neutral:
                    r += [IndexAction(j)]
                    break
        return r

    def execute_action(self, pp: int, action):
        for i in range(self.rows):
            if self.board[i][action.index] == neutral:
                self.board[i][action.index] = pp
                break

    def finalized(self, pp):
        def check_iter(start, direction):
            current_connect = 0
            current_pp = neutral
            i, j = start
            while 0 <= i < self.rows and 0 <= j < self.cols and current_connect < self.connect:
                if self.board[i][j] != neutral:
                    if self.board[i][j] == current_pp:
                        current_connect += 1
                    else:
                        current_connect = 1
                        current_pp = self.board[i][j]
                else:
                    current_connect = 0
                    current_pp = neutral
                i += direction[0]
                j += direction[1]
            if current_connect >= self.connect:
                return True, current_pp
            else:
                return False, None
        # check horizontal
        r = []
        for i in range(self.rows):
            r += [check_iter((i, 0), (0, 1))]
            r += [check_iter((i, 0), (1, 1))]
            r += [check_iter((i, 0), (-1, 1))]
        # check vertical
        for j in range(self.cols):
            r += [check_iter((0, j), (1, 0))]
            r += [check_iter((0, j), (1, 1))]
            r += [check_iter((0, j), (1, -1))]
        for done, pp in r:
            if done:
                return True, pp
        return len(self.get_actions(pp)) == 0, None

    def __repr__(self):
        r = ""
        str_dict = {-1: " ", 0: "x", 1: "o"}
        for row in self.board[::-1]:
            s = ""
            for c in row:
                s += str_dict[c]
            r += s+"\n"
        return r[:-1]
