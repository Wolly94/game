from game import AlternateTurnGame
from helper import User, RandomPlayer
from mcts import MCTSPlayer

from tictactoe import TTTState
from connectn import ConnectNState

board1 = TTTState()
game1 = AlternateTurnGame(2, board1)
board2 = ConnectNState()
game2 = AlternateTurnGame(2, board2)

#p1 = MCTSPlayer()
players = [RandomPlayer(), RandomPlayer()]
players = [MCTSPlayer(), MCTSPlayer()]
print(game1.play_games(1, players))


#print(game2.play_games(1000, [RandomPlayer()]*2))
#print(game1.play_games(1000, [RandomPlayer()]*2))
