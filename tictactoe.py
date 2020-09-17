from abstract_classes import BoardState, PlayerIndex
from helper import IndexAction

board_size = 9
neutral = -1
winning_sequences = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]

class TTTState(BoardState):
    def __init__(self, board = None):
        self.board = board
        if board is None:
            self.reset()

    def reset(self):
        self.board = [neutral for _ in range(board_size)]

    def get_actions(self, pp):
        return [IndexAction(i) for i, v in enumerate(self.board) if v == neutral]

    def execute_action(self, pp, action):
        self.board[action.index] = pp

    def finalized(self, pp):
        for seq in winning_sequences:
            p = self.board[seq[0]]
            if p != neutral and len([i for i in seq if self.board[i] == p]) == 3:
                return True, PlayerIndex(p)
        return len(self.get_actions(pp)) == 0, None

    def __repr__(self):
        #return repr(self.board)
        r = ""
        str_dict = {-1: " ", 0: "x", 1: "o"}
        for i in range(3):
            s = ""
            for j in range(3):
                s += str_dict[self.board[3*i+j]]
            r += s+"\n"
        return r[:-1]
