import math
import numpy as np
from copy import deepcopy
from game import AlternateTurnGame, Player, PlayerIndex, Winner
from helper import RandomPlayer

number_of_iterations = 1000

class Node:
    def __init__(self, state: AlternateTurnGame, parent = None):
        self.state = state
        self.parent = parent
        self.c = 2
        self.children = None
        self.visited = False
        self.statistics = {PlayerIndex(i): 0 for i in range(state.n)}
        self.statistics[None] = 0
        self.statistics["visits"] = 0

    def make_root(self):
        self.parent = None

    def Q(self, player):
        return self.statistics[player]+self.statistics[None]*1.0/self.state.n

    def N(self):
        return self.statistics["visits"]

    def search(self, n: int):
        m = self.N()
        print("mcts iterations:", n-m)
        for _i in range(n-m):
            #if (i+1)%100 == 0:
            #    print(n, "simulations left")
            leaf = self.traverse()
            simulation_result = leaf.rollout()
            leaf.backpropagate(simulation_result)
        return self.best_action()

    def best_uct(self):
        def uct_value(tup):
            n = tup[1]
            return n.Q(self.state.current_player)/n.N() + self.c* math.sqrt(math.log(self.N())/n.N())
        return max(self.children, key=uct_value)

    def best_action(self):
        return max(self.children, key=lambda tup: tup[1].Q(self.state.current_player)/tup[1].N() if tup[1].N() > 0 else 0)[0]

    def traverse(self): # return node with visited == False
        if self.state.done:
            return self
        if self.children is None:
            self.children = []
            for action in self.state.board.get_actions(self.state.current_player):
                new_state = deepcopy(self.state)
                new_state.next_state(action)
                new_node = Node(new_state, self)
                self.children.append((action, new_node))
        if len(self.children) == 0:
            return self
        l = list(filter(lambda n: not n[1].visited, self.children))
        if len(l) == 0:
            return self.best_uct()[1].traverse()
        else:
            i = int(np.random.randint(0, len(l)))
            return l[i][1]

    def rollout(self) -> Winner:
        self.visited = True
        if self.state.done:
            return self.state.winner
        s = deepcopy(self.state)
        r = s.play([RandomPlayer()]*self.state.n, False)
        return r

    def update_stats(self, result):
        self.statistics["visits"] += 1
        self.statistics[result] += 1

    def backpropagate(self, result):
        self.update_stats(result)
        if self.parent is not None:
            self.parent.backpropagate(result)


class MCTSPlayer(Player):
    def __init__(self):
        self.node = None

    def select_action(self, actions, state):
        if self.node is None or state.last_actions is None or len(state.last_actions) < state.n:
            self.node = Node(deepcopy(state))
        else:
            for action in state.last_actions:
                found = False
                for tup in self.node.children:
                    if tup[0] == action:
                        self.node = tup[1]
                        found = True
                        break
                if not found:
                    print("resetted")
                    self.node = Node(deepcopy(state))
                    break
            self.node.make_root()
        action = self.node.search(number_of_iterations)
        return action
