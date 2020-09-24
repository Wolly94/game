from typing import List
from abstract_classes import Action, Player
import random


class IndexAction(Action):
    def __init__(self, index):
        self.index = index

    def __repr__(self):
        return str(self.index)

    def __eq__(self, other):
        return self.index == other.index


class RandomPlayer(Player):
    def select_action(self, actions, game):
        return random.choice(actions)


class User(Player):
    def select_action(self, actions: List[Action], game):
        print("current game state:\n"+repr(game))
        print("possible actions are:", actions)
        print("Enter '#' + index of the action you want to choose, or just write down the action:")
        while True:
            inp = input()
            if len(inp) == 0:
                continue
            if inp[0] == '#':
                try:
                    i = int(inp[1:])
                    if 0 <= i < len(actions):
                        return actions[i]
                    else:
                        print("Not a valid number, please try again!")
                except ValueError:
                    print("Invalid input, please try again!")
            else:
                try:
                    action = next(x for x in actions if str(x) == inp)
                    return action
                except StopIteration:
                    print("Invalid input, please try again!")
