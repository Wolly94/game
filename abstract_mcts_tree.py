from copy import deepcopy
from abc import ABC, abstractmethod
import numpy as np

class Node(ABC):
    @abstractmethod
    def is_leaf(self) -> bool:
        pass

    # number of visits
    @abstractmethod
    def N(self):
        pass

    # eval of current node
    @abstractmethod
    def Q(self):
        pass

    @abstractmethod
    def winner(self):
        pass

    @abstractmethod
    def update_stats(self, result):
        pass

    @abstractmethod
    def finish_random(self):
        pass

    def __init__(self, parent = None):
        self.visited = False
        self.parent = parent
        self.c = 2
        # list of (action, new_node)
        self.children = None

    def make_root(self):
        self.parent = None

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
            return n.Q()/n.N() + self.c * math.sqrt(math.log(self.N())/n.N())
        return max(self.children, key=uct_value)

    def best_action(self):
        return max(self.children, key=lambda key: key[1].Q()/key[1].N() if key[1].N() > 0 else 0)[0]

    def traverse(self): # return node with visited == False or a leaf
        if self.is_leaf():
            return self
        if len(self.children) == 0:
            return self
        l = list(filter(lambda n: not n[1].visited, self.children))
        if len(l) == 0:
            return self.best_uct()[1].traverse()
        else:
            i = int(np.random.randint(0, len(l)))
            return l[i]

    def rollout(self):
        self.visited = True
        if self.is_leaf():
            return self.winner()
        r = self.finish_random()
        return r

    def backpropagate(self, result):
        self.update_stats(result)
        if self.parent is not None:
            self.parent.backpropagate(result)

    def render(self):
        for tup in self.children:
            print(tup[1])
