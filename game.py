from copy import deepcopy
from time import sleep
import random

VISUAL_DELAY = 0.04
SPACER = 50  # amount of lines to print to space boards out


class Minesweeper:

    def __init__(self, rows: int, cols: int, mine_spawn: float, chars_config: dict = None):
        # config dictionary that holds the actual character strings mappings
        # for what character to display for each board element; e.g. mine = 'X'
        self.chars = {'tile': '□',
                      'mine': '☹',
                      'zero': ' ',
                      'flag': '+',
                      'maybe': '?'
                      } if chars_config is None else chars_config
        # █🅱️💥💣
        #(R, A, D, H, Q respectively to reveal, arm or disarm a tile, to get help or to quit), optionally followed by coordinates
        self.set_up_game(rows, cols, mine_spawn)

    def set_up_game(self, rows, cols, prob):
        """ Sets up new game. """
        # settings for the game board
        self.rows = rows
        self.cols = cols
        self.area = rows * cols
        self.prob = prob

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

    def reset_game(self):
        """ Resets values of the same game. """
        self.mask = self.gen_mask_board()  # just resets mask board

    def iswin(self):
        """ Checks if the player won. """
        count = 0
        # counts number of number tiles
        for r in range(self.rows):
            for c in range(self.cols):
                if type(self.mask[r][c]) is int:
                    count += 1
        # checks if total tiles - number tiles is equal to bombs, this means you found everything
        if self.area - count == self.mine_count:
            return True
        else:
            return False

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

    def display_game(self, border: bool = False):
        """ Iterates through game board and prints tiles. (so numbers and mines) """
        if border:
            print('-'*(self.cols*2+3))
        for r in range(self.rows):
            if border:
                print('|', end=' ')
            for c in range(self.cols):
                tile = self.game[r][c]
                if tile is True:  # mine
                    print(self.chars['mine'], end=' ')
                elif tile == 0:  # empty tile (zero)
                    print(self.chars['zero'], end=' ')
                elif type(tile) is int:  # number tile
                    print(str(tile), end=' ')
            if border:
                print('|', end='')
            print()
        if border:
            print('-'*(self.cols*2+3))

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
                # if tile is True:  # mine
                #     print(self.chars['mine'], end=' ')
                if tile is False:  # unexplored tile
                    print(self.chars['tile'], end=' ')
                elif tile == 0:  # empty tile (zero)
                    print(self.chars['zero'], end=' ')
                elif type(tile) is int:  # number tile
                    print(str(tile), end=' ')
                else:  # other chars: flag, maybe, etc.
                    print(tile, end=' ')
            print()

    def floodfill(self, r, c):
        """ Flood fill algorithm: recursively reveals tiles on the board. """
        for rr in range(r-1, r+2):
            for cc in range(c-1, c+2):
                self.reveal(rr, cc)

    def reveal(self, r, c):
        """ Reveals tile and flood fills if needed. """
        if self.bounds(r, c) and self.mask[r][c] is False:  # only reveals if in bounds and unexplored
            tile = self.game[r][c]  # gets the tile from the game board
            self.mask[r][c] = tile  # reveals tile on mask
            if tile == 0:  # recurses/floodfill if tile is 0
                space()
                self.display_mask()
                sleep(VISUAL_DELAY)  # NOTE: this is purely cosmetic so that I could see the game recursing
                self.floodfill(r, c)

    def flag(self, r, c):
        """ Sets tile to flag so users can mark tiles as mines. """
        if self.mask[r][c] == self.chars['flag']:  # unflags if already flagged
            self.mask[r][c] = False
        elif self.mask[r][c] is False:  # can only flag unexplored tiles
            self.mask[r][c] = self.chars['flag']  # flags
        else:
            # can't flag already revealed tiles
            pass

    def maybe(self, r, c):
        """ Sets tile to maybe so users can mark tiles as possible mines. """
        if self.mask[r][c] == self.chars['maybe']:  # unmaybes if already maybeged
            self.mask[r][c] = False
        elif self.mask[r][c] is False:  # can only maybe unexplored tiles
            self.mask[r][c] = self.chars['maybe']  # maybes
        else:
            # can't maybe already revealed tiles
            pass

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
        if r < 0 or r >= self.rows or c < 0 or c >= self.cols:  # ripped from Guha's water.c floodfill function
            return False  # meaning the coord is outside of the board
        else:
            return True  # coord is within the board


def space():
    print('\n'*SPACER)
