from copy import deepcopy
import random
from re import T
# FIXME: when you flag and unflag a number it disappears

class Minesweeper:

    def __init__(self, rows: int, cols: int, mine_spawn: float, chars_config: dict = None):
        # config dictionary that holds the actual character strings mappings
        # for what character to display for each board element; e.g. mine = 'X'
        self.chars = {'tile': '□',
                      'mine': '🅱️',  # *
                      'zero': ' ',
                      'flag': '+',
                      'maybe': '?'
                      } if chars_config is None else chars_config
        # █🅱️
        #(R, A, D, H, Q respectively to reveal, arm or disarm a tile, to get help or to quit), optionally followed by coordinates

        # settings for the game board
        self.rows = rows
        self.cols = cols
        self.prob = mine_spawn

        # board guides
        self.rguide = self.make_guide(rows)
        self.cguide = self.make_guide(cols)

        # the different boards (external viewed by player and internal only viewed by code)
        self.mines = self.gen_mine_board()  # just the mines, stored in code form
        self.game = self.gen_game_board()  # internal board, stored in code form
        self.mask = self.gen_mask_board()  # the board as seen by the user, stored as strings

        # goes through the newly created mine board and counts number of mines generated
        self.mine_count = 0
        for mine_row in self.mines:
            self.mine_count += mine_row.count(True)

    def gen_mine_board(self) -> list:
        """ Generates a mine board based on probability given. (just True and False) """
        return [[random.random() < self.prob for i in range(self.cols)] for j in range(self.rows)]

    def gen_game_board(self) -> list:
        """ Generates a gameboard by overwriting a copy of the mine board. (adds mine counts) """
        game_board = deepcopy(self.mines)  # deep copies mine board to write over it

        for r in range(self.rows):
            for c in range(self.cols):
                # for non-mine tiles (number tiles)
                if game_board[r][c] is False:
                    game_board[r][c] = 0  # sets counter to 0
                    # (rr, cc) indexes neighboring tiles and counts mines
                    for rr in range(r-1, r+2):
                        for cc in range(c-1, c+2):
                            if self.bounds(rr, cc):  # if cell is within bounds
                                # increments main tile if that surrounding tile has a mine
                                if self.mines[rr][cc]:
                                    game_board[r][c] += 1

        return game_board

    def gen_mask_board(self) -> list:
        """ Generates a mask board to display to the user: tiles, armed flags, maybe flags, etc. (strings) """
        return [[False for i in range(self.cols)] for j in range(self.rows)]

    def display_mines(self, ascii: bool = False):
        """ Iterates through mine board and prints mine status. """
        if ascii:  # prints mines as their mask symbol
            for r in range(self.rows):
                for c in range(self.cols):
                    print(self.chars['mine'] if self.mines[r][c] else self.chars['tile'], end=' ')
                print()  #                        do I print it as empty tile or as zero ___^
        if not ascii:  # prints mines as boolean values
            for r in range(self.rows):
                for c in range(self.cols):
                    print(self.mines[r][c], end=' ')
                print()

    def display_game(self):
        """ Iterates through game board and prints tiles. (so numbers and mines) """
        for r in range(self.rows):
            for c in range(self.cols):
                tile = self.game[r][c]
                if tile is True:  # mine
                    print(self.chars['mine'], end=' ')
                elif tile == 0:  # empty tile (zero)
                    print(self.chars['zero'], end=' ')
                elif type(tile) is int:  # number tile
                    print(str(tile), end=' ')
            print()

    def display_mask(self):
        """ Iterates through mask board and prints tiles. (what user sees) """
        print('   ', end='')  # the little corner spacer before the X-axis guide

        # == X-AXIS ==

        # prints the numbers first
        for num in self.cguide:
            print(str(num), end=' ')
        print()

        # then prints the little ticks
        print('   ', end='')
        for i in range(self.cols):
            print('| ', end='')
        print()

        # == Y-AXIS & BOARD ==

        for r in range(self.rows):
            print(f'{self.cguide[r]}--', end='')  # prints the guide: number + tick
            # goes through every tile in the row and gets mask symbol
            for c in range(self.cols):
                tile = self.mask[r][c]
                if tile is True:  # mine
                    print(self.chars['mine'], end=' ')
                elif tile is False:  # unexplored tile
                    print(self.chars['tile'], end=' ')
                elif tile == 0:  # empty tile (zero)
                    print(self.chars['zero'], end=' ')
                elif type(tile) is int:  # number tile
                    print(str(tile), end=' ')
                else:  # other chars: flag, maybe, etc.
                    print(tile, end=' ')
            print()

    def cascade(self, r, c):
        """ Flood fill algorithm. """
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
        tile = self.game[r][c]
        self.mask[r-1][c-1] = tile
        if tile == 0:
            self.cascade(r, c)

    # allows the user to flag unopened tiles as a mine if speculated to be
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

    def make_guide(self, length: int):
        """ Makes board guide based on given length. """
        repeat = [1, 2, 3, 4, 5, 6, 7, 8, 9, '█']  # █ is the 10s marker
        rem = length % 10
        guide = []

        for i in range(length//10):  # extends the guide by 10 everytime
            guide.extend(repeat)
        for i in range(rem):  # extends the last bit that doesn't quite make 10
            guide.append(repeat[i])

        return guide

    def bounds(self, r, c) -> bool:
        """ Checks if given coord is within board bounds. """
        if r < 0 or r >= self.rows or c < 0 or c >= self.rows:  # ripped from Guha's water.c floodfill function
            return False  # meaning the coord is outside of the board
        else:
            return True  # coord is within the board
