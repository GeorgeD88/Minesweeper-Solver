from collections.abc import Generator
from collections import deque
from copy import deepcopy
from time import sleep
import random
import sys


HELPER_DELAY = 0.01  # this delay is to give the code a 1ms bump after printing the board in hopes of getting rid of the jittery visuals
VISUAL_DELAY = 0.01#12
SPACER = 50  # amount of lines to print to space boards out
ADJACENT_COORDS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
# ADJACENT_COORDS = [(r, c) for r in range(-1, 2) for c in range(-1, 2)]
# ADJACENT_COORDS.pop(4)

class Minesweeper:

    def __init__(self, rows: int, cols: int, mine_spawn: float, chars_config: dict = None):
        # config dictionary that holds the actual character strings mappings
        # for what character to display for each board element; e.g. mine = 'X'
        self.chars = {'tile': '▢',#□
                      'mine': '☹',
                      'zero': ' ',
                      'flag': '+',
                      'maybe': '?'
                      } if chars_config is None else chars_config
        # █🅱️💥💣
        self.set_up_game(rows, cols, mine_spawn)

    def set_up_game(self, rows, cols, prob):
        """ Sets up new game. """
        # settings for the game board
        self.rows = rows
        self.cols = cols
        self.area = rows * cols
        self.prob = prob

        # board coord guides
        self.rguide = self.make_guide(rows)
        self.cguide = self.make_guide(cols)

        # initialize mine count which will be incremented when generating mine board
        self.mine_count = 0

        # the different boards (external viewed by player and internal only viewed by code)
        self.mines = self.gen_mine_board()  # just the mines, stored in code form
        self.game = self.gen_game_board()  # internal board, stored in code form
        self.mask = self.gen_mask_board()  # the board info available to the user so far

        # NOTE: old method of counting mines which did it after generating the mines, new code does it while generating it so there's not repeat
        # goes through the newly created mine board and counts number of mines generated
        """ for mine_row in self.mines:
            self.mine_count += mine_row.count(True) """
        self.mask_tile_count = 0

    def reset_game(self):
        """ Resets mask board of game, without regenerating actual game board. """
        self.mask = self.gen_mask_board()

    def regen_game(self):
        """ Regenerates game board, so completely new game basically. """
        # regenerates all the boards
        self.mines = self.gen_mine_board()  # regenerates new mine board
        self.game = self.gen_game_board()  # regenerates game board
        self.mask = self.gen_mask_board()  # regenerate mask board

        # goes through the newly created mine board and counts number of mines generated
        self.mine_count = 0
        for mine_row in self.mines:
            self.mine_count += mine_row.count(True)
        self.mask_tile_count = 0

    def iswin(self) -> bool:
        """ Checks if the player won. """
        return self.area - self.mask_tile_count == self.mine_count

    def isloss(self, row: int, col: int) -> bool:
        """ Checks if coord choice is a loss. """
        # lack of bomb is more likely, we use that as a shortcircuit
        return self.is_new(row, col) and self.game[row][col] is True

    def gen_mine_board(self) -> list:
        """ Generates a mine board based on probability given. (just True and False) """

        # this way creates the list while counting mines at the same time
        scratch_mine_board = []

        for _row in range(self.rows):
            scratch_mine_board.append([])
            for _col in range(self.cols):
                if random.random() < self.prob:
                    scratch_mine_board.append(True)
                    self.mine_count += 1
                else:
                    scratch_mine_board.append(False)

        return scratch_mine_board

        # create list inline
        # return [[random.random() < self.prob for i in range(self.cols)] for j in range(self.rows)]

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

    def empty_spot(self, row, col):
        """ Checks if given coords is an empty tile (0) or not. """
        return self.game[row][col] == 0

    def find_empty_drop(self, row, col):
        """ Regenerates game board until empty spot is found. """
        while not self.empty_spot(row, col):
            # print('POOUUOOP')
            self.regen_game()

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

    def display_game(self, border: bool = True):
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

    # NOTE: older version
    # def old_display_mask(self):
    #     """ Iterates through mask board and prints tiles. (what user sees) """
    #     print('   ', end='')  # the little corner spacer before the X-axis guide

    #     # == X-AXIS ==

    #     # prints the numbers first
    #     for num in self.cguide:
    #         print(str(num), end=' ')
    #     print()

    #     # then prints the little ticks
    #     print('   ', end='')
    #     for i in range(self.cols):
    #         print('| ', end='')
    #     print()

    #     # == Y-AXIS & BOARD ==

    #     for r in range(self.rows):
    #         print(f'{self.rguide[r]}--', end='')  # prints the guide: number + tick
    #         # goes through every tile in the row and gets mask symbol
    #         for c in range(self.cols):
    #             tile = self.mask[r][c]
    #             # if tile is True:  # mine
    #             #     print(self.chars['mine'], end=' ')
    #             if tile is False:  # unexplored tile
    #                 print(self.chars['tile'], end=' ')
    #             elif tile == 0:  # empty tile (zero)
    #                 print(self.chars['zero'], end=' ')
    #             elif isinstance(tile, int):  # number tile
    #                 print(str(tile), end=' ')
    #             elif isinstance(tile, str):  # should only happen if altered by solver for color
    #                 print(tile, end=' ')
    #             else:  # other chars: flag, maybe, etc.
    #                 print(tile, end=' ')
    #         print()

    def display_mask(self):
        """ Iterates through mask board and prints tiles. (what user sees) """

        # == X-AXIS ==
        constructed = '   '

        # prints the numbers first
        for num in self.cguide:
            constructed += str(num) + ' '
        constructed += '\n'

        # then prints the little ticks
        constructed += '   '
        for i in range(self.cols):
            constructed += '| '
        constructed += '\n'

        # == Y-AXIS & BOARD ==

        for r in range(self.rows):

            constructed += f'{self.rguide[r]}--'  # prints the guide: number + tick

            # goes through every tile in the row and gets mask symbol
            for c in range(self.cols):
                tile = self.mask[r][c]
                if tile is False:  # unexplored tile
                    constructed += self.chars['tile']
                elif tile == 0:  # empty tile (zero)
                    constructed += self.chars['zero']
                elif isinstance(tile, int):  # number tile
                    constructed += str(tile)
                elif isinstance(tile, str):  # should only happen if altered by solver for color
                    constructed += tile
                else:  # other chars: flag, maybe, etc.
                    constructed += tile
                constructed += ' '  # adds space between every character added

            constructed += '\n'  # adds new line at end of the row

        # print(constructed)
        sys.stdout.write(constructed)

    def print_board(self):
        """ Prints a space and then the board. """
        space()
        self.display_mask()
        sleep(HELPER_DELAY)

    def reveal(self, r, c):
        """ Helper function to reveal without starting a recursion. """
        if self.bounds(r, c) and self.is_new(r, c):  # only runs if within bounds and not already explored (memoization)
            tile = self.just_reveal(r, c)
            if tile == 0:  # recurses/floodfill if tile is 0
                self.print_board()
                sleep(VISUAL_DELAY)  # NOTE: this is purely cosmetic so that I could see the game recursing
                self.level_order_fill(r, c) #self.bfs_fill(r, c)  # NOTE: change this to change flood fill algorithm used for game

    # FLOOD FILL ALGORITHM
    def floodfill(self, r, c):
        """ Flood fill algorithm: recursively reveals tiles on the board. """
        for rr in range(r-1, r+2):
            for cc in range(c-1, c+2):
                self.flood_reveal(rr, cc)

    def flood_reveal(self, r, c):
        """ Reveals tile and flood fills if needed. """
        if self.bounds(r, c) and self.is_new(r, c):  # only runs if within bounds and not already explored (memoization)
            tile = self.game[r][c]  # gets the tile from the game board
            if tile is True:
                return False
            self.mask[r][c] = tile  # reveals tile on mask
            self.mask_tile_count += 1  # increments counter of mask tiles
            if tile == 0:  # recurses/floodfill if tile is 0
                self.print_board()
                sleep(VISUAL_DELAY)  # NOTE: this is purely cosmetic so that I could see the game recursing
                self.floodfill(r, c)

    # BREADTH FIRST SEARCH ALGORITHM RELATED CODE
    def adjacent_nodes(self, curr: tuple[int, int]) -> Generator[tuple[int, int]]:
        """ Returns the coords of the surrounding nodes. """
        for offset_c in ADJACENT_COORDS:
            yield self.offset_coord(curr, offset_c)

        """ for offset_c in ADJACENT_COORDS:
            adj_coord = self.offset_coord(curr, offset_c)
            if self.bounds(*adj_coord):
                yield adj_coord """

    def offset_coord(self, coord: tuple[int, int], offset: tuple[int, int]) -> tuple[int, int]:
        """ Returns a coord with the given offset. """
        return tuple(x + y for x, y in zip(coord, offset))

    def bfs_fill(self, r, c):
        """ Breadth first search implementation of floodfill. """
        queue = deque([(r, c)])  # use append to enqueue popleft to dequeue
        processed = set()  # hashset containing nodes already processed
        processed.add((r, c))

        while len(queue) > 0:  # while queue not empty
            curr = queue.popleft()

            # if this node hasn't been processed or revealed in the past
            if curr not in processed and self.is_new(*curr):
                tile = self.just_reveal(*curr)  # process node
                processed.add(curr)  # add to processed

                self.print_board()
                sleep(VISUAL_DELAY)  # NOTE: this is purely cosmetic so that I could see the game recursing

                if tile != 0:
                    continue

            # check next breadth of nodes
            for adj in self.adjacent_nodes(curr):
                # the bounds makes sure it doesn't try searching outside the board
                # NOTE: consider checking if adj in queue, but may take O(n) time so could be just as bad as leaving it in queue
                if adj not in processed and adj not in queue and self.bounds(*adj) and self.is_new(*adj):  # is not bomb, or int?
                    queue.append(adj)

    def level_order_fill(self, r, c):
        """ Level order traversal (BFS) implementation of floodfill. """
        queue = deque([(r, c)])  # use append to enqueue popleft to dequeue
        processed = {(r, c)}  # hashset containing nodes already processed

        # while there are nodes queued up to explore
        while len(queue) > 0:
            breadth = len(queue)

            # iterate through breadth
            for _ in range(breadth):
                curr = queue.popleft()

                # reveal/process node
                self.just_reveal(*curr)

                # don't traverse past this tile if it's not a 0 (it's a chain)
                if self.game[curr[0]][curr[1]] != 0:
                    continue

                # add next breadth of nodes
                for adj in self.adjacent_nodes(curr):
                    # the bounds makes sure it doesn't try searching outside the board
                    # NOTE: consider checking if adj in queue, but may take O(n) time so could be just as bad as leaving it in queue
                    # print(adj)
                    if adj not in processed and self.bounds(*adj):#self.is_new(*adj):  # is not bomb, or int?
                        queue.append(adj)
                        processed.add(adj)

            # only show changes visually after the whole breadth has been
            self.print_board()
            sleep(VISUAL_DELAY)  # NOTE: this is purely cosmetic so that I could see the game recursing

            """  # if this node hasn't been processed or revealed in the past
                if curr not in processed and self.is_new(*curr):
                    tile = self.just_reveal(*curr)  # process node
                    processed.add(curr)  # add to processed

                    self.print_board()
                    sleep(VISUAL_DELAY)  # NOTE: this is purely cosmetic so that I could see the game recursing
            """
    def just_reveal(self, r, c) -> int or bool:
        """ Reveals tile and bfs fills if needed (returns True if number). """
        tile = self.game[r][c]  # gets the tile from the game board
        self.mask[r][c] = tile  # reveals tile on mask
        self.mask_tile_count += 1  # increments counter of mask tiles
        return tile

    def flag(self, r, c):
        """ Sets tile to flag so users can mark tiles as mines. """
        if self.mask[r][c] == self.chars['flag']:  # unflags if already flagged
            self.mask[r][c] = False
        elif self.is_new(r, c):  # can only flag unexplored tiles
            self.mask[r][c] = self.chars['flag']  # flags
        else:
            # can't flag already revealed tiles
            pass

    def maybe(self, r, c):
        """ Sets tile to maybe so users can mark tiles as possible mines. """
        if self.mask[r][c] == self.chars['maybe']:  # unmaybes if already maybeged
            self.mask[r][c] = False
        elif self.is_new(r, c):  # can only maybe unexplored tiles
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

    def is_new(self, r, c) -> bool:
        """ Checks if given tile has not been explored. """
        return self.mask[r][c] is False


def space():
    print('\n'*SPACER)
