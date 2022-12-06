# interface
import pygame
from gui_game import Minesweeper, Node
from gui_colors import *
from constants import *

# data structures
from collections import deque

# dev stuff
from pprint import PrettyPrinter


pp = PrettyPrinter().pprint  # for dev purposes


class Solver(Minesweeper):

    def __init__(self, rows: int = ROWS, cols: int = COLS, mine_spawn: float or int = MINE_SPAWN, win_height: int = WIN_HEIGHT, win_title: str = WIN_TITLE):
        super().__init__(rows, cols, mine_spawn, win_height, win_title)

        self.first_drop = None
        """ NOTE: going to store the first drop coord in a class variable because we might
        need it a few times and it makes it easier than having to pass it around functions. """

        # solver colors
        self.CURRENT = DARK_PURPLE_TINT
        self.VISITED = DARK_YELLOW_TINT
        self.SOLVED = DARK_GREEN_TINT

    """ TODO
    I have to decide how I want to start the solver integration.
    like if I want to be able to continue the solver from wherever the user presses key,
    I have to figure out how I want to grab the existing information.
    or maybe I'll decide to not be able to continue the user's work and I can only activate it
    from the starting empty drop/pool.
    """

    def init_solver(self):
        """ Initialize solver, startup code for bot. """
        self.solved_count = self.flagged_count = 0
        # add solver attributes to every node in the grid
        for node in self.loop_all_nodes():
            node.solved = False

    # TODO: maybe put init_solver in main solver function and just make it part of the algorithm function.
    def solve_board(self):
        """ Solver algorithm, the whole bot algorithm. """
        pass

    def run_solver(self):
        """ Run solver by initializing bot, then running it. """
        self.init_solver()
        self.solve_board()
