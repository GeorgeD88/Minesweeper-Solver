from collections.abc import Generator
from pprint import PrettyPrinter
from collections import deque
from copy import deepcopy
from time import sleep
import random
import sys


# == VISUALIZATION CONSTANTS ==
HELPER_DELAY = 0.01  # this delay is to give the code a 1ms bump after printing the board in hopes of getting rid of the jittery visuals
VISUAL_DELAY = 0.08#12
SPACER = 50  # amount of lines to print to space boards out

# == GAME CONSTANTS ==
ADJACENT_COORDS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
""" ADJACENT_COORDS = [(r, c) for r in range(-1, 2) for c in range(-1, 2)]
ADJACENT_COORDS.pop(4) """

pp = PrettyPrinter().pprint  # for dev purposes


class Minesweeper:

    def __init__(self, rows: int, cols: int, mine_spawn: float, chars_config: dict = None):
        """ config dictionary that holds the character strings
        that map to each game/board element; e.g. mine = 'X' """
        self.chars = {'tile': '▢',#□
                      'mine': '☹',
                      'zero': ' ',
                      'flag': '+',
                      'maybe': '?'
                      } if chars_config is None else chars_config  # if custom characters are provided
        # other chars I might use: █🅱️💥💣

        self.set_up_game(rows, cols, mine_spawn)

    def set_up_game(self, rows, cols, prob):
        """ Sets up new game. """
        # settings/properties for the game board
        self.rows = rows
        self.cols = cols
        self.area = rows * cols  # number of total tiles
        self.prob = prob  # probability of mine spawn

        # board coordinate guides
        self.rguide = self.make_guide(rows)
        self.cguide = self.make_guide(cols)

        # NOTE: I started initializing mine_count and mask_tile_count in their respective board generation functions

        # the different boards (external viewed by player and internal only viewed by code)
        self.mines = self.gen_mine_board()  # boolean matrix representing the board's mines
        self.game = self.gen_game_board()  # internal board, stores the mines and numbers
        self.mask = self.gen_mask_board()  # keeps track of what the player has revealed/flagged so far

    def reset_game(self):
        """ Resets mask board, without regenerating game board.
            Essentially resetting same game back to beginning. """
        self.mask = self.gen_mask_board()

    def regen_game(self):
        """ Regenerates all boards, completely new game.
            Since we're regenerating the mines and recounting on the mine board,
            it's a whole different game (not same as reset_game()). """
        self.mines = self.gen_mine_board()
        self.game = self.gen_game_board()
        self.mask = self.gen_mask_board()

    def iswin(self) -> bool:
        """ Checks if the player won by comparing mine count to unrevealed count. """
        return self.area - self.revealed_count == self.mine_count

    def isloss(self, row: int, col: int) -> bool:
        """ Checks if coord choice is a loss (mine). """

        """ NOTE: checks if the tile is unrevealed first because if you're still
        playing the game and the tile is already revealed then there's no way it's a loss now.
        also you can't reveal already revealed tiles. """

        return self.is_new(row, col) and self.game[row][col] is True

    def gen_mine_board(self) -> list[list]:
        """ Generates a mine board (boolean matrix) based on given probability. """
        self.mine_count = 0  # stores total number of mines
        mine_board = []

        # NOTE: using underscore to signify that this value isn't actually used and is just for iterating
        for _row in range(self.rows):
            mine_board.append([])  # append new row list
            for _col in range(self.cols):
                # randomly generates bomb
                if random.random() < self.prob:
                    mine_board[-1].append(True)
                    self.mine_count += 1
                else:
                    mine_board[-1].append(False)

        return mine_board

    # TODO: mine board generation by number of mines
    # def gen_mine_board_by_count(self, mines: int) -> list[list]:
    #     """ Generates a mine board (boolean matrix) based on desired mine count. """
    #     self.mine_count = mines  # stores total number of mines
    #     mine_board = [[False for c in range(self.cols)] for r in range(self.rows)]

    #     # generate 'mines' number of random coords
    #     for _ in range(mines):
    #         # NOTE: this is a do while. you write the do code, then you exit when it becomes opposite of your desire while
    #         while True:
    #             rr, cc = random.randrange(self.rows), random.randrange(self.cols)
    #             if mine_board[rr][cc] is False:
    #                 mine_board[rr][cc] = True
    #                 break

    #     return mine_board

    def gen_game_board(self) -> list[list]:
        """ Generates a game board by traversing copy of mine board and writing mine counts. """
        game_board = deepcopy(self.mines)  # deep copies mine board to write over it

        """ m is main tile and n are the adjacent tiles to tile m
        N N N
        N M N
        N N N
        """

        # loops for M tile
        for r in range(self.rows):
            for c in range(self.cols):
                # non-mine tiles are replaced with their mine count
                if game_board[r][c] is False:
                    game_board[r][c] = 0  # sets counter to 0
                    # indexes neighboring tiles (N tiles of M) and counts mines
                    for rr, cc in self.adjacent_nodes((r, c)):
                        # increments tile mine count if adjacent tile contains a mine
                        if self.bounds(rr, cc):  # ensures tile is within bounds first
                            if self.mines[rr][cc] is True:
                                game_board[r][c] += 1

        return game_board

    def gen_mask_board(self) -> list[list]:
        """ Generates a mask board to display to the user (tiles, flags, etc.). """
        self.revealed_count = 0  # keeps count of how many tiles were revealed (not flagged)
        return self.gen_boolean_matrix()

    def gen_boolean_matrix(self) -> list[list]:
        """ Generates a boolean matrix of False values. """
        return [[False for c in range(self.cols)] for r in range(self.rows)]

    def find_empty_drop(self, row, col):
        """ Regenerates game board until empty spot is found. """
        while not self.empty_spot(row, col):
            self.regen_game()

    def display_mines(self, ascii: bool = False):
        """ Iterates through mine board and prints mine status (dev function). """
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
        """ Iterates through game board and prints contents (mines and numbers). """
        # prints border around board
        if border:  # top border
            print('-'*(self.cols*2+3))

        for r in range(self.rows):
            if border:  # left border
                print('|', end=' ')

            for c in range(self.cols):
                tile = self.game[r][c]

                if tile is True:  # mine
                    print(self.chars['mine'], end=' ')
                elif tile == 0:  # empty tile (zero)
                    print(self.chars['zero'], end=' ')
                elif type(tile) is int:  # number tile
                    print(str(tile), end=' ')

            if border:  # right border
                print('|', end='')

            print()

        if border:  # bottom border
            print('-'*(self.cols*2+3))

    def display_mask(self):
        """ Iterates through mask board and prints tiles (what user sees). """

        # == horizontal guide ==
        constructed = '   '

        # prints the numbers first
        for num in self.cguide:
            constructed += str(num) + ' '
        constructed += '\n'

        # then prints the little ticks
        constructed += '   '
        for _ in range(self.cols):
            constructed += '| '
        constructed += '\n'

        # == vertical guide + board contents ==

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
        # NOTE: trying stdout instead of print to try to speed up printing
        sys.stdout.write(constructed)

    def print_board(self):
        """ Prints a space to clear the output, prints mask, then delays. """
        space()
        self.display_mask()
        sleep(HELPER_DELAY)

    def reveal(self, r, c):
        """ Helper function to reveal and floodfill if needed. """
        # only runs if within bounds and not already explored/opened
        if self.bounds(r, c) and self.is_new(r, c):
            tile = self.just_reveal(r, c)  # reveal the tile first

            """ NOTE: prints board because for cases where floodfill isn't run,
            you won't see this reveal until the next floodfill """
            self.print_board()
            sleep(VISUAL_DELAY)

            # then checks if floodfill is needed
            if tile == 0:
                # NOTE: change this to change which flood fill algorithm is used for the game
                self.level_order_fill(r, c) #self.bfs_fill(r, c)

    # FLOOD FILL ALGORITHMS
    def floodfill(self, r, c):
        """ Flood fill algorithm: recursively reveals tiles on the board. """
        for rr in range(r-1, r+2):
            for cc in range(c-1, c+2):
                self.flood_reveal(rr, cc)

    def flood_reveal(self, r, c):
        """ Reveals tile and flood fills if needed. """
        if self.bounds(r, c) and self.is_new(r, c):  # only runs if within bounds and not already explored (to prevent cycles)
            tile = self.just_reveal(r, c)

            if tile == 0:  # recurses/floodfill if tile is 0
                self.print_board()
                sleep(VISUAL_DELAY)  # NOTE: this is purely cosmetic so that I could see the game recursing
                self.floodfill(r, c)

    def bfs_fill(self, r, c):
        """ Breadth first search implementation of floodfill. """
        queue = deque([(r, c)])  # append (enqueue) and popleft (dequeue)
        discovered = {(r, c)}  # hashset containing nodes already discovered

        # while queue not empty (there's still nodes to traverse)
        while len(queue) > 0:
            curr = queue.popleft()  # pop next node to process

            # process node
            tile = self.just_reveal(*curr)
            # displays changes after every tile reveal
            self.print_board()
            sleep(VISUAL_DELAY)

            # don't traverse past this tile if it's not a 0 (you hit a chain, you wanna stay within the lake)
            if tile != 0:
                continue

            # add adjacent nodes to queue
            for adj in self.adjacent_nodes(curr):
                """ NOTE: only adds node if it isn't already queued to process,
                and if node isn't new then it was processed during a different run of this function. """
                if adj not in discovered and self.is_new(*adj):
                    discovered.add(adj)
                    queue.append(adj)

    def level_order_fill(self, r, c):
        """ Level order traversal (BFS) implementation of floodfill. """
        queue = deque([(r, c)])  # use append to enqueue popleft to dequeue
        discovered = {(r, c)}  # hashset containing nodes already discovered

        # while queue not empty (there's still nodes to traverse)
        while len(queue) > 0:
            breadth = len(queue)  # get length of next breadth of nodes

            # iterate through nodes one breadth at a time
            for _ in range(breadth):
                curr = queue.popleft()  # pop next node to process

                # reveal/process node
                tile = self.just_reveal(*curr)
                # NOTE: doesn't display changes until whole breadth as been processed

                # don't traverse past this tile if it's not a 0 (you hit a chain, you wanna stay within the lake)
                if tile != 0:
                    continue

                # add next breadth of nodes to queue
                for adj in self.adjacent_nodes(curr):
                    """ NOTE: only adds node if it isn't already queued to process,
                    and if node isn't new then it was processed during a different run of this function. """
                    if adj not in discovered and self.is_new(*adj):
                        discovered.add(adj)
                        queue.append(adj)

            # only show changes visually after the whole breadth has been processed
            self.print_board()
            sleep(VISUAL_DELAY)

    def adjacent_nodes(self, curr: tuple[int, int]) -> Generator[tuple[int, int]]:
        """ Returns the coords of the adjacent nodes (sides and corners). """
        for offset_c in ADJACENT_COORDS:
            adj_coord = self.offset_coord(curr, offset_c)
            """ NOTE: a reason I may not want to check if adjacent nodes are within bounds
            is because I simply want this function to return adjacent coordinates,
            and not alter that in any way like checking if they're within bounds.
            that may also be why I had this function overwritten in the solver file
            to not check for bounds, maybe I needed that functionality for some algorithm.
            NOTE: I'm making descriptive note of this incase some bug comes up later that could be related to this. """
            if self.bounds(*adj_coord) is True:
                yield adj_coord

    def offset_coord(self, coord: tuple[int, int], offset: tuple[int, int]) -> tuple[int, int]:
        """ Returns a coord with the given offset. """
        return tuple(crd + ofst for crd, ofst in zip(coord, offset))

    def just_reveal(self, r, c) -> int or bool:
        """ Only reveal tile and returns tile's content. """
        tile = self.game[r][c]  # gets the tile from the game board
        self.mask[r][c] = tile  # reveals the tile on mask
        self.revealed_count += 1  # increments counter of mask tiles
        return tile

    def flag(self, r, c):
        """ Sets tile to flag so users can mark suspected mine tiles. """
        if self.mask[r][c] == self.chars['flag']:  # unflags if already flagged
            self.mask[r][c] = False
        elif self.is_new(r, c):  # can only flag unexplored tiles
            self.mask[r][c] = self.chars['flag']  # flags
        # else: can't flag already revealed tiles

    def maybe(self, r, c):
        """ Sets tile to maybe so users can mark tiles as possible mines. """
        if self.mask[r][c] == self.chars['maybe']:  # unmaybes if already maybed
            self.mask[r][c] = False
        elif self.is_new(r, c):  # can only maybe unexplored tiles
            self.mask[r][c] = self.chars['maybe']  # maybes
        # else: can't maybe already revealed tiles

    def make_guide(self, length: int) -> list:
        """ Builds board guide string based on given length. """
        repeat = [1, 2, 3, 4, 5, 6, 7, 8, 9, '█']  # █ is the 10s marker
        rem = length % 10
        guide = []

        # extends the guide by 10 every time
        for i in range(length//10):
            guide.extend(repeat)

        # extends the last bit that doesn't quite make 10
        guide.extend(repeat[:rem])

        return guide

    def bounds(self, r, c) -> bool:
        """ Checks if given coord is within board bounds. """
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_new(self, r, c) -> bool:
        """ Checks if given tile has not been explored/revealed on the mask. """
        return self.mask[r][c] is False

    def empty_spot(self, row, col) -> bool:
        """ Checks if given coords is an empty tile (0) or not. """
        return self.game[row][col] == 0


def space():
    """ Prints huge block of newlines to "flush" the console output. """
    print('\n'*SPACER)
