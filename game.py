from copy import deepcopy
from abstract_classes import BoardState, PlayerIndex, Action, Player, Winner
from helper import RandomPlayer
from typing import Tuple, List

HistoryKnot = Tuple[BoardState, PlayerIndex, Action]


class History:
    def __init__(self):
        self.l = []


class Game:
    pass


class AlternateTurnGame(Game):
    def __init__(self, n: int, board: BoardState):
        self.board = board
        self.n = n
        self.current_player = None
        self.done, self.winner = None, None
        self.last_actions = None
        self.reset()

    def reset(self):
        self.current_player = PlayerIndex(0)
        self.finalized = (False, None)
        self.done, self.winner = False, None
        self.last_actions = []
        self.board.reset()

    def next_player(self):
        self.current_player = PlayerIndex((self.current_player+1)%self.n)

    def random_outcome(self) -> Winner:
        game_copy = deepcopy(self)
        players = [RandomPlayer()]*self.n
        return game_copy.play(players)

    # mb check if len(players) == self.n
    def play(self, players: List[Player], track: bool = False):
        if track:
            history = History()
        self.done, self.winner = self.board.finalized(self.current_player)
        while not self.done:
            pl = players[self.current_player]
            actions = self.board.get_actions(self.current_player)
            action = pl.select_action(actions, self)
            if track:
                knot = (deepcopy(self.board), self.current_player, action)
                history.l.append(knot)
            self.board.execute_action(self.current_player, action)
            self.last_actions += [action]
            if len(self.last_actions) > self.n:
                self.last_actions = self.last_actions[1:]
            self.next_player()
            self.done, self.winner = self.board.finalized(self.current_player)
        if track:
            return self.winner, history
        else:
            return self.winner

    def play_games(self, n: int, players: List[Player]):
        statistics = {PlayerIndex(i): 0 for i in range(self.n)}
        statistics[None] = 0
        for _i in range(n):
            self.reset()
            winner = self.play(players)
            statistics[winner] += 1
        return statistics

    def __repr__(self):
        return repr(self.board)
