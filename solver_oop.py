from copy import deepcopy
import random


# Solver class to create objects representing a solver/the game it's solving.
# This class makes it easier for me to get data on the game it's playing and such.
class Solver:

    def __init__(self, rows, cols, chars_config) -> object:
        # config dictionary that holds the actual character strings mappings
        # for what character to display for each board element; e.g. bomb = 'X'
        self.chars = chars_config

        # settings for the game board
        self.rows = rows
        self.cols = cols

        # the different boards (external viewed by player and internal only viewed by code)
        #bombs = [[False for i in range(cols+2)] for j in range(rows+2)]
        self.board = 0  # stores the board as the game presents it to the user
        self.bombs_known = 0
        self.bombs_speculated = 0

        self.bomb_count = 0
        for bomb_row in self.bombs:
            self.bomb_count += bomb_row.count(True)

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
        return [[False for i in range(self.cols)] for j in range(self.rows)]

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
        repeat = [1, 2, 3, 4, 5, 6, 7, 8, 9, '█']
        rem = self.cols % 10
        guide = []
        for i in range(int(self.cols-rem)//10):
            guide.extend(repeat)
        for i in range(rem):
            guide.append(repeat[i])

        print('   ', end='')
        for num in guide:
            print(str(num) + ' ', end='')
        print()
        print('   ', end='')
        for i in range(self.cols):
            print('| ', end='')
        print()

        rem = self.rows % 10
        guide = []
        for i in range(int(self.rows-rem)//10):
            guide.extend(repeat)
        for i in range(rem):
            guide.append(repeat[i])

        for r in range(self.rows):
            print(f'{guide[r]}--', end='')
            for c in range(self.cols):
                cell = self.mask[r][c]
                if cell is True:
                    print(self.chars['bomb'] + ' ', end='')
                elif cell is False:
                    print(self.chars['tile'] + ' ', end='')
                elif cell == 0:
                    print(self.chars['zero'] + ' ', end='')
                elif type(cell) is int:
                    print(str(cell) + ' ', end='')
                else:
                    print(cell + ' ', end='')
            print()

    def cascade(self, r, c):
        for rr in range(r-1, r+2):
            for cc in range(c-1, c+2):
                checking = self.game[rr][cc]
                if checking is False or self.mask[rr-1][cc-1] is not False:  # meaning this is part of the no-no border or it's already been checked
                    continue
                # this part checks if the mask is 0 so it's checking if it was already cascaded/discovered
                # try:
                # elif :  # if this tile was already revealed then don't cascade from it
                #     continue
                # except IndexError:
                #     continue
                self.mask[rr-1][cc-1] = checking
                if checking == 0:
                    self.cascade(rr, cc)

    # checks the pressed tile and decides if it's a regular tile and then proceeds as needed
    def reveal(self, r, c):
        cell = self.game[r][c]
        self.mask[r-1][c-1] = cell
        if cell == 0:
            self.cascade(r, c)

    # allows the user to flag unopened tiles as a bomb if speculated to be
    def flag(self, r, c):
        if self.mask[r-1][c-1] == self.chars['flag']:  # unflags if already flagged
            self.mask[r-1][c-1] = False
        else:
            self.mask[r-1][c-1] = self.chars['flag']  # flags

    def maybe(self, r, c):
        if self.mask[r-1][c-1] == self.chars['maybe']:  # unmaybes if already flagged
            self.mask[r-1][c-1] = False
        else:
            self.mask[r-1][c-1] = self.chars['maybe']  # maybes
