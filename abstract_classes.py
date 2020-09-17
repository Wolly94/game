from random import choice
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, NewType

PlayerIndex = int
Winner = Optional[PlayerIndex]
Finalized = Tuple[bool, Winner]

class Action(ABC):
    pass


class BoardState(ABC):
    @abstractmethod
    def finalized(self, i: PlayerIndex) -> Finalized: # updates self.winner and self.done
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def execute_action(self, i: PlayerIndex, action: Action):
        pass

    @abstractmethod
    def get_actions(self, player_to_move: PlayerIndex) -> List[Action]:
        pass


class Player(ABC):
    @abstractmethod
    def select_action(self, actions: List[Action], game: 'Game'):
        pass
