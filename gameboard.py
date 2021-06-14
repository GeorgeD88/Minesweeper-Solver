from copy import deepcopy
import random
from typing import Sequence


# Minesweeper class to create objects representing a whole game with the boards.
# This class allows me to easily run methods on the game instead of using global variables.
class Minesweeper:

    def __init__(self, rows, cols, prob, chars_config=None) -> object:
        # config dictionary that holds the actual character strings mappings
        # for what character to display for each board element; e.g. bomb = 'X'
        self.chars = {'tile': '□', 'bomb': '🅱️', 'zero': ' ', 'armed': '#', 'maybe': '?'} if chars_config is None else chars_config
        #                                   █🅱️
        #(r, a, d, h, q respectively to reveal, arm or disarm a tile, to get help or to quit), optionally followed by coordinates

        # settings for the game board
        self.rows = rows
        self.cols = cols
        self.prob = prob

        # the different boards (external viewed by player and internal only viewed by code)
        #bombs = [[False for i in range(cols+2)] for j in range(rows+2)]
        self.bombs = self.create_bomb_board()  # just the bombs, stored in code form
        self.game = self.create_game_board()  # internal board, stored in code form
        self.mask = self.create_mask_board()  # the board as seen by the user, stored as strings

    # creates a bomb board: tiles (False) and bombs (True)
    def create_bomb_board(self) -> list:
        # puts random bombs everywhere including border
        new_bomb_board = [[random.random() < self.prob for i in range(self.cols+2)] for j in range(self.rows+2)]

        # overwrites the border's True/False mixed bombs with just False so that it doesn't mess up the count
        for c in range(self.cols+2):  # top and bottom row
            new_bomb_board[0][c] = False
            new_bomb_board[-1][c] = False
        for r in range(1, self.rows+1):  # left and right columns besides the overlap
            new_bomb_board[r][0] = False
            new_bomb_board[r][-1] = False
        return new_bomb_board

    # creates a game board from a previously created bomb board: tiles (int of adjacent bombs) and bombs (True)
    def create_game_board(self) -> list:
        # defines the board by starting with a copy of the bomb board that it can edit
        game_board = deepcopy(self.bombs)
        #board = [[0 for i in range(c+2)] for j in range(r+2)]
        # goes through every element and replaces every regular
        # tile with the number of bombs in the adjacent cent tiles.
        for r in range(1, self.rows+1):
            for c in range(1, self.cols+1):
                if game_board[r][c] is False:  # meaning it's not a bomb
                    game_board[r][c] = 0
                    # (rr, cc) indexes neighboring cells.
                    for rr in range(r-1, r+2):
                        for cc in range(c-1, c+2):
                            cell = self.bombs[rr][cc]
                            if cell:
                                game_board[r][c] += 1
        return game_board

    # creates a mask board to display to the user: tiles, armed flags, maybe flags, etc. (strings)
    def create_mask_board(self) -> list:
        regular_tile = self.chars['tile']
        return [[regular_tile for i in range(self.cols)] for j in range(self.rows)]

    def display_bombs(self):
        for r in range(1, self.rows+1):
            for c in range(1, self.cols+1):
                print(self.bombs[r][c] + ' ', end='')
            print()

    def display_game(self):
        for r in range(1, self.rows+1):
            for c in range(1,self.cols+1):
                cell = self.game[r][c]
                if cell is True:
                    print(self.chars['bomb'] + ' ', end='')
                elif cell == 0:
                    print(self.chars['zero'] + ' ', end='')
                elif type(cell) is int:
                    print(str(cell) + ' ', end='')
            print()

    def display_mask(self):
        for r in range(self.rows):
            for c in range(self.cols):
                print(self.mask[r][c] + ' ', end='')
            print()


# # # goes through every individual element in the bomb array and runs a random number to determine whether
# # # or not to insert a bomb there; the bomb is inserted if the number is within the given probability.
# # # OLD COMMENT: bombs is [1..rows][1..cols]; the border is used to handle boundary cases.
# # bombs = [[False for i in range(cols+2)] for j in range(rows+2)]

# # for r in range(1, rows+1):
# #     for c in range(1, cols+1):
# #         bombs[r][c] = (random.random() < prob)

# # # initializes a 2d array to hold the solution board as a rows+2 * cols+2 array,
# # # each regular tile contains the number of adjacent tiles with bombs.
# # # INTERNAL BOARD
# # board = [[0 for i in range(cols+2)] for j in range(rows+2)]

# # # goes through every element and replaces every regular
# # # tile with the number of bombs in the adjacent tiles.
# # for r in range(1, rows+1):
# #     for c in range(1, cols+1):
# #         # (rr, cc) indexes neighboring cells.
# #         for rr in range(r-1, r+2):
# #             for cc in range(c-1, c+2):
# #                 if bombs[rr][cc]:
# #                     board[r][c] += 1


# # # TODO: figure out characters to use
# # mask = [['. ' for i in range(cols+2)] for j in range(rows+2)]

# # prints the mask board that the player sees
# def display_mask():
#     for r in range(1, rows+1):
#         for c in range(1, cols+1):
#             if mask[r][c]:
#                 print('* ', end="")
#             else:
#                 print('. ', end="")
#         print()

# # prints the internal board that only the code sees
# def display_board():
#     print()
#     for r in range(1, rows+1):
#         for c in range(1, cols+1):
#             if bombs[r][c]:
#                 print('* ', end="")
#             else:
#                 print(str(board[r][c]) + ' ', end="")
#         print()


# checks if the tile contains a bomb or not
def check_tile(r, c):
    pass

# checks the pressed tile and decides if it's a regular tile and then proceeds as needed
def press(r, c):
    pass
# TODO: do the recursive function for opening a tile surrounded by 0s fro a while

# allows the user to flag unopened tiles as a bomb if speculated to be
def flag(r, c, maybe: bool = False):
    """
        Flags hidden tiles on player's board as surely bomb or possibly a bomb.

        TODO: ARGS
    """

    pass