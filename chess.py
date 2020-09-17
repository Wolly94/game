from copy import deepcopy
from typing import Tuple, List, Dict, Optional
from abstract_classes import Action, BoardState
import itertools

neutral = 0
pawn = 1
knight = 2
bishop = 3
rook = 4
queen = 5
king = 6
units = [pawn, knight, bishop, rook, queen, king]
repr_map = {pawn: 'P', knight: 'N', bishop: 'B', rook: 'R', queen: 'Q', king: 'K'}
repr_map2 = {-v: repr_map[v].lower() for v in repr_map.keys()}
repr_map.update(repr_map2)
repr_map[neutral] = " "

rows = list(range(1, 9))
cols = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
order = [rook, knight, bishop, queen, king, bishop, knight, rook]
board_size = 8

# l is list of lists
def concat_lists(l):
    r = []
    for e in l:
        r += e
    return r

def player_sign(pp: int): # 0, 1 -> 1, -1
    return 1-2*pp

def sign_to_player(sign: int): # 1, -1 -> 0, 1
    return 1-int((sign+1)/2)

def switch_player(pp: int): # 0, 1 -> 1, 0
    return (pp+1)%2

# for second player, we use the negative number

class ChessAction(Action):
    def __init__(self, starting_field, ending_field, state = None):
        self.repr = ""
        self.starting_field = starting_field
        self.ending_field = ending_field
        self.set_repr(state)

    def set_repr(self, state = None):
        if state is None:
            r = cols[self.starting_field[1]]+str(rows[self.starting_field[0]])
            r += cols[self.ending_field[1]]+str(rows[self.ending_field[0]])
            self.repr = r
        else:
            i, j = self.starting_field
            v = state.board[i][j]
            r = repr_map[abs(v)]
            r += cols[j]+str(rows[i])
            if state.board[self.ending_field[0]][self.ending_field[1]] != neutral:
                r += "x"
            r += cols[self.ending_field[1]]+str(rows[self.ending_field[0]])
            self.repr = r
            # TODO check if there exists another move starting from another field and check for check or checkmate

    def execute(self, state):
        i, j = self.starting_field
        k, l = self.ending_field
        state.board[k][l] = state.board[i][j]
        state.board[i][j] = neutral
        for pos in [self.starting_field, self.ending_field]:
            if pos in state.rochade_rooks_pos:
                state.rochade_rooks_pos.remove(pos)
            elif pos in state.rochade_kings_pos:
                state.rochade_kings_pos.remove(pos)

    def __repr__(self):
        return self.repr

class Promotion(ChessAction):
    def __init__(self, starting_field, ending_field, target_v: int, state = None):
        self.target_v = target_v
        super().__init__(starting_field, ending_field, state)

    def set_repr(self, state = None):
        super().set_repr(state)
        self.repr += repr_map[self.target_v]

    def execute(self, state):
        super().execute(state)
        i, j = self.ending_field
        state.board[i][j] *= self.target_v

class PawnAdvance(ChessAction):
    def execute(self, state):
        super().execute(state)
        state.en_passant_pawn_position = self.ending_field


class EnPassant(ChessAction):
    def execute(self, state):
        super().execute(state)
        i, j = state.en_passant_pawn_position
        state.board[i][j] = neutral
        state.en_passant_pawn_position = None


class Rochade(ChessAction):
    def __init__(self, starting_field, ending_field, rook_field, state):
        self.rook_field = rook_field
        super().__init__(starting_field, ending_field, state)

    def set_repr(self, state):
        r = "O-O"
        if abs(self.starting_field[1]-self.rook_field[1]) == 4:
            r += "-O"
        self.repr = r

    def execute(self, state):
        super().execute(state)
        i, j = self.starting_field
        j2 = self.rook_field[1]
        direction = 1 if j < j2 else -1
        state.board[i][j+direction] = state.board[i][j2]
        state.board[i][j2] = neutral
        

class ChessState(BoardState):
    def __init__(self):
        self.board = None
        self.en_passant_pawn_position = None
        self.rochade_rooks_pos = None
        self.rochade_kings_pos = None
        self.reset()

    def clear(self):
        self.board = [[0 for _ in cols] for _ in rows]
        self.en_passant_pawn_position = None

    def reset(self):
        self.clear()
        for direction in [1, -1]:
            pp = sign_to_player(direction)
            row = pp*(board_size-1)
            for j in range(board_size):
                self.board[row+direction][j] = direction*pawn
                self.board[row][j] = direction*order[j]
        self.rochade_rooks_pos = []
        for i in [0, 7]:
            for j in [0, 7]:
                self.rochade_rooks_pos += [(i, j)]
        self.rochade_kings_pos = [(0, 4), (7, 4)]

    def get_attacked_fields_from(self, position) -> List[Tuple[int, int]]:
        r = []
        v = self.board[position[0]][position[1]]
        if abs(v) in [bishop, rook, queen, king]:
            directions = []
            if abs(v) in [bishop, queen, king]:
                directions += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            if abs(v) in [rook, queen, king]:
                directions += [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for x, y in directions:
                i, j = position[0]+x, position[1]+y
                while 0 <= i < board_size and 0 <= j < board_size:
                    r += [(i, j)]
                    if self.board[i][j] != neutral or abs(v) == king:
                        break
                    i += x
                    j += y
        elif abs(v) in [knight]:
            for x in [-1, 1]:
                for y in [-2, 2]:
                    r += [(position[0]+x, position[1]+y), (position[0]+y, position[1]+x)]
            r = list(filter(lambda pos: 0 <= pos[0] < board_size and 0 <= pos[1] < board_size, r))
        elif abs(v) in [pawn]:
            direction = 1 if v > 0 else -1
            if position[1] > 0:
                r += [(position[0]+direction, position[1]-1)]
            if position[1] < board_size - 1:
                r += [(position[0]+direction, position[1]+1)]
        return r

    def get_attacked_fields(self) -> Dict[int, Dict[Tuple[int, int], List[Tuple[int, int]]]]:
        d = {0: {}, 1: {}}
        for i, row in enumerate(self.board):
            for j, v in enumerate(row):
                if v == 0:
                    continue
                pp = 0 if v > 0 else 1
                d[pp][(i, j)] = self.get_attacked_fields_from((i, j))
        return d


    def get_actions(self, pp: int) -> List[Action]:
        r = []
        a_field_dict = self.get_attacked_fields()
        for starting_pos, list_of_ending_pos in a_field_dict[pp].items():
            v = self.board[starting_pos[0]][starting_pos[1]]
            if abs(v) is pawn:
                direction = 1 if v > 0 else -1
                i, j = starting_pos
                promotion = i+direction == (board_size-1)*switch_player(pp)
                poss_ending_cols = []
                if self.board[i+direction][j] is neutral:
                    poss_ending_cols += [j]
                    if i == (board_size-1)*pp + direction and self.board[i+2*direction][j] is neutral:
                        r += [PawnAdvance(starting_pos, (i+2*direction, j), self)]
                for ending_pos in list_of_ending_pos:
                    v2 = self.board[ending_pos[0]][ending_pos[1]]
                    if v*v2 < 0:
                        poss_ending_cols += [ending_pos[1]]
                    elif v*v2 == 0 and (ending_pos[0]-direction, ending_pos[1]) == self.en_passant_pawn_position:
                        r += [EnPassant(starting_field, ending_field, state)]
                for j in poss_ending_cols:
                    if promotion:
                        for value in [knight, bishop, rook, queen]:
                            r += [Promotion(starting_pos, (i+direction, j), value, self)]
                    else:
                        r += [ChessAction(starting_pos, ending_pos, self)]
            else:
                for ending_pos in list_of_ending_pos:
                    v2 = self.board[ending_pos[0]][ending_pos[1]]
                    if v*v2 <= 0: # in other words, ending_pos is neutral or enemy
                        r += [ChessAction(starting_pos, ending_pos, self)]
            # check for Rochade
            if abs(v) == king:
                enemy_attacks = concat_lists(list(a_field_dict[switch_player(pp)].values()))
                if starting_pos in self.rochade_kings_pos:
                    for rook_pos in self.rochade_rooks_pos:
                        if rook_pos[0] == starting_pos[0]:
                            direction = 1 if rook_pos[1]-starting_pos[1] > 0 else -1
                            i, j = starting_pos
                            possible = True
                            for pos in [(i, j), (i, j+direction), (i, j+2*direction)]:
                                if pos in enemy_attacks or (pos[1] != j and self.board[pos[0]][pos[1]] != neutral):
                                    possible = False
                                    break
                            if possible:
                                r += [Rochade(starting_pos, (starting_pos[0], starting_pos[1]+2*direction), rook_pos, self)]
        result = []
        for action in r:
            dupl = deepcopy(self)
            dupl.execute_action(action)
            if not dupl.king_in_check(pp):
                result += [action]
        return result
            
    def king_in_check(self, pp: int):
        attacked_fields = self.get_attacked_fields()
        enemy_attacks = []
        [enemy_attacks.extend(el) for el in attacked_fields[switch_player(pp)].values()]
        for pos in enemy_attacks:
            if self.board[pos[0]][pos[1]] == king*player_sign(pp):
                return True
        return False

    def finalized(self, pp):
        return len(self.get_actions(pp)) == 0, switch_player(pp) if self.king_in_check(pp) else None

    def execute_action(self, action: ChessAction):
        action.execute(self)

    def __repr__(self):
        r = ""
        for row in self.board:
            s = ""
            for v in row:
                s += repr_map[v]
            r = s+"\n"+r
        return r[:-1]

    def display_actions(self, pp: int):
        actions = self.get_actions(pp)
        actions = list(map(lambda act: act.smart_repr(self), actions))
        print("possible actions:", actions)

    def render(self):
        print("render attacked fields")
        attacked_fields = self.get_attacked_fields()[1]
        attacked_fields = concat_lists(list(attacked_fields.values()))
        r = ""
        for i, row in enumerate(self.board):
            s = ""
            for j, v in enumerate(row):
                if v == 0 and (i, j) in attacked_fields:
                    s += "x"
                else:
                    s += repr_map[v]
            r = s+"\n"+r
        return r[:-1]


s = ChessState()
s.clear()
s.board[0][0] = rook
s.board[0][4] = king
s.board[5][4] = -king
s.board[1][5] = -knight
print(s)
print(s.render())
print(s.get_actions(0))
actions = s.get_actions(0)
#print(s.board)
#print(s.render())
#print(s.get_actions(1))
print(s.king_in_check(0))
print(s.king_in_check(1))
#s.display_actions(0)
