# interface
import pygame
from gui_colors import *
from constants import *

# data structures
from collections import deque

# dev stuff
from typing import Generator
from pprint import PrettyPrinter

# miscellaneous
import random


pp = PrettyPrinter().pprint  # for dev purposes


class Node:

    def __init__(self, visualizer, row: int, col: int, value: bool or int):
        self.parent = visualizer  # visualizer class that holds these nodes
        self.size = visualizer.cell_size  # side length of the cell

        self.x, self.y = col * self.size, row * self.size  # coord in the pygame window
        self.row, self.col = row, col  # coord of node on the board

        self.state = self.parent.UNREVEALED  # current state/color of the node
        self.value = value  # minesweeper tile value (0 to 9 or mine)

    def get_coord(self) -> tuple[int, int]:
        """ Returns node's coordinate. """
        return (self.row, self.col)

    def reveal(self):
        """ Set node state to revealed, or to mine if its value is a mine. """
        self.state = self.parent.REVEALED if self.value is not None else self.parent.MINE

    def unreveal(self):
        """ Set node state to unrevealed. """
        self.state = self.parent.UNREVEALED

    def is_unrevealed(self) -> bool:
        """ Returns whether node is unrevealed/unexplored. """
        return self.state == self.parent.UNREVEALED

    def is_mine(self) -> bool:
        """ Returns whether node is a mine. """
        return self.value is True

    def is_empty(self) -> bool:
        """ Returns whether node is an empty area (zero). """
        return self.value == 0


class Minesweeper:
    """ Game logic + visual (graphical), NOT INPUT. From here, we add the user input through a subclass (in another file) to play the game. """

    def __init__(self, rows: int = 50, cols: int = 80, mine_spawn: float = 0.15, win_height: int = WIN_HEIGHT, win_title: str = 'Minesweeper 💣🧹', color_mappings: dict = None):
        # TODO: add option to generate mines by mine count, not just probability

        # pygame window dimensions
        self.win_height = win_height  # window height
        self.cell_size = self.win_height // rows  # visual cell size
        self.cell_grid_size = self.cell_size * 0.56  # actual grid length (aesthetic purposes)
        self.grid_space = (self.cell_size - self.cell_grid_size) // 2  # the empty spaces in grid sides
        self.win_width = self.cell_size * cols  # window width

        # pygame window (everything is drawn here)
        self.win = pygame.display.set_mode((self.win_width, self.win_height))
        pygame.display.set_caption(win_title)
        self.reveal_state = True  # whether clicking will reveal or flag (true = reveal, false = flag)

        # sets each color mapping to default value if custom color aren't provided
        if color_mappings is None:
            self.GRID_LINE = GRAY
            self.TILE_NUMBER = WHITE  # tile foreground color (tile number)
            self.REVEALED = DARK_GRAY  # tile background color (behind number)
            self.UNREVEALED = VIOLET  # color theme
            self.MINE = DARK_RED
        # else color mappings were provided so sets values of provided colors
        else:
            self.GRID_LINE = GRAY if 'GRID_LINE' not in color_mappings else color_mappings['GRID_LINE']
            self.TILE_NUMBER = WHITE if 'TILE_NUMBER' not in color_mappings else color_mappings['TILE_NUMBER']
            self.REVEALED = DARK_GRAY if 'REVEALED' not in color_mappings else color_mappings['REVEALED']
            self.UNREVEALED = VIOLET if 'UNREVEALED' not in color_mappings else color_mappings['UNREVEALED']
            self.MINE = DARK_RED if 'MINE' not in color_mappings else color_mappings['MINE']

        # board properties
        self.rows, self.cols = rows, cols  # board dimensions
        self.area = rows * cols  # number of total tiles
        self.prob = mine_spawn  # probability of mine spawn

        # game setup
        self.initialize_board()

    # === GAME SETUP FUNCTIONS ===
    def generate_mine_matrix(self) -> list[list]:
        """ Generates a matrix of mines (booleans) based on game's mine spawn probability. """
        self.mine_count = 0  # stores total number of mines
        mine_board = []

        for _ in range(self.rows):
            mine_board.append([])  # append new row list
            for _ in range(self.cols):
                # randomly generates mine
                if random.random() < self.prob:
                    mine_board[-1].append(True)
                    self.mine_count += 1
                else:
                    mine_board[-1].append(False)

        return mine_board

    def write_mine_counts(self):
        """ Adds the mine counts to a board with already initialized nodes and mines. """
        for r in range(self.rows):
            for c in range(self.cols):
                if self.get_node(r, c).is_mine():  # skip mines
                    continue
                # traverses the nodes adjacent to this node
                for adj in self.adjacent_nodes(self.get_node(r, c)):
                    # if the adjacent node is a mine, increments current node's mine count
                    if adj.is_mine():
                        self.get_node(r, c).value += 1

    def initialize_board(self):
        """ Generates a board by generating mines then writing mine counts. """
        """ NOTE: compared to my previous implementations of minesweeper,
        here I have a step that only runs during the initial board generation,
        which is the initialization of all the nodes. if I want to reset,
        then that just involves resetting the values of the nodes, but I never
        have to reinitialize the nodes. """
        mines = self.generate_mine_matrix()  # matrix of values, not node objects
        self.board = []

        # initializes board with node objects, sets value to 0 if not a mine
        for r in range(self.rows):
            self.board.append([])  # append new list for next row
            for c in range(self.cols):  # append new node to last list
                self.board[-1].append(Node(self, r, c, True if mines[r][c] is True else 0))

        # traverse board and count mines
        self.count_adjacent_mines()

    def new_game(self):
        """ Generates new game by regenerating mines/counts and unrevealing all nodes. """
        mines = self.generate_mine_matrix()  # regenerates mines

        # traverse board and set values according to new mines
        for r in range(self.rows):
            for c in range(self.cols):
                self.get_node(r, c).unreveal()
                self.get_node(r, c).value = True if mines[r][c] is True else 0

        # traverse board and count mines
        self.count_adjacent_mines()

    def reset_game(self):
        """ Sets all tiles back to unrevealed but doesn't regenerate game board values. """
        for r in range(self.rows):
            for c in range(self.cols):
                self.get_node(r, c).unreveal()

    # === HELPER FUNCTIONS ===
    def gen_matrix(self, default=None) -> list[list]:
        """ Generates a 2D array the size of the board consisting of the given default value. """
        nested_arr = [] if default is None else [default]*self.cols
        return [nested_arr for _ in range(self.rows)]

    def get_node(self, r: int, c: int) -> Node:
        """ Returns the node at the given coord. """
        return self.board[r][c]

    def adjacent_coords(self, r: int, c: int) -> Generator[tuple[int, int]]:
        """ Returns the coords adjacent to the given coord. """
        for offset in ADJACENT_COORDS:
            adj_coord = self.offset_coord((r, c), offset)
            if self.bounds(*adj_coord) is True:
                yield adj_coord

    def adjacent_nodes(self, node: Node) -> Generator[Node]:
        """ Generates the nodes adjacent to the given node. """
        for offset in ADJACENT_COORDS:
            adj = self.offset_coord(node.get_coord(), offset)  # gets coord from node and offsets
            # yields adjacent node if it's in bounds
            if self.in_bounds(*adj):
                yield self.get_node(*adj)

    def offset_coord(self, coord: tuple[int, int], offset: tuple[int, int]) -> tuple[int, int]:
        """ Returns a coord offset by the given offset. """
        return tuple(crd + ofst for crd, ofst in zip(coord, offset))

    def in_bounds(self, r: int, c: int) -> bool:
        """ Returns whether the given coord is within bounds. """
        return 0 <= r < self.rows and 0 <= c < self.cols

    # === SOMETHING (GETTERS?) ===
    def is_win(self) -> bool:
        """ Checks if the player won by comparing mine count to unrevealed count. """
        # NOTE: it's important to remember that you win by revealing all open spaces and not by flagging all the mines
        return self.area - self.revealed_count == self.mine_count

    def is_loss(self, row: int, col: int) -> bool:
        """ Checks if coord choice is a loss (mine). """
        # NOTE: I should remove the is new and have that checked externally, because really the input should be sanitized before.
        return self.is_new(row, col) and self.get_node is True

    # === PYGAME FUNCTIONS ===
    # NOTE: when drawing unrevealed nodes, draw without grid so it's one seamless pool of color.
    def draw_node(self, node):
        """ Draws given node onto pygame window. """
        pygame.draw.rect(self.win, node.state, (node.x, node.y, self.cell_size, self.cell_size))

    def draw_node_grid(self, node):
        """ Only given node's grid lines. """
        # draw top line
        pygame.draw.line(self.win, self.GRID_LINE, (node.x+self.grid_space, node.y), (node.x+self.cell_size-self.grid_space, node.y))

        # draw left line
        pygame.draw.line(self.win, self.GRID_LINE, (node.x, node.y+self.grid_space), (node.x, node.y+self.cell_size-self.grid_space))

        # draw bottom line
        pygame.draw.line(self.win, self.GRID_LINE, (node.x+self.grid_space, node.y+self.cell_size-1), (node.x+self.cell_size-self.grid_space, node.y+self.cell_size-1))

        # draw right line
        pygame.draw.line(self.win, self.GRID_LINE, (node.x+self.cell_size-1, node.y+self.grid_space), (node.x+self.cell_size-1, node.y+self.cell_size-self.grid_space))

    def delay(self, wait: float = WAIT):
        """ Delay some amount of time, for animation/visual purposes. """
        pygame.time.delay(int(wait*1000))

    def update_node(self, node, wait: float = WAIT):
        """ Draws given node and draws grid based on state, then updates display. """
        self.draw_node(node)
        if not node.is_unrevealed():
            self.draw_node_grid(node)
        if wait is not None:
            self.delay(wait)
        pygame.display.update()

    def update_revealed(self, node, wait: float = WAIT):
        """ Draws given node and its grid, then updates display. """
        self.draw_node(node)
        self.draw_node_grid(node)
        if wait is not None:
            self.delay(wait)
        pygame.display.update()

    def update_unrevealed(self, node, wait: float = WAIT):
        """ Draws given node w/o grid, then updates display. """
        self.draw_node(node)
        if wait is not None:
            self.delay(wait)
        pygame.display.update()

    def draw(self):
        """ Redraws all elements onto window (updates display). """
        # fill with with white
        self.win.fill(WHITE)

        # goes through every node in the grid and draws it
        for row in self.grid:
            for node in row:
                self.draw_node(node)
                self.draw_node_grid(node)

        pygame.display.update()

    # === GAME FUNCTIONS ===
    def reveal(self, node: Node):
        """  """
        pass

    def flag(self, node: Node):
        """  """
        pass

    # TODO: implement maybe flag later
    # def maybe(self, node: Node):
    #     """  """
    #     pass

    # flood fill algorithms
    def level_order_floodfill(self, start: Node):
        """ Flood fills board using level order traversal starting at given node """
        pass
    def initialize_game(self):
        """ Startup code for game. """
        pass

    def game_loop(self):
        """ Update loop for game. """
        # TODO: you can press a button at any time similar to the visualizer, and it runs the solver, regardless of where you are in the game
        pass

    def run_game(self):
        """ Runs startup code and starts update loop. """
        pass