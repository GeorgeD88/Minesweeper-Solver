# interface
from gui_minesweeper import Minesweeper, Node
from constants import *

# data structures
from collections import deque

# dev stuff
from typing import Generator
from pprint import PrettyPrinter

# miscellaneous
import random


pp = PrettyPrinter().pprint  # for dev purposes


class User(Minesweeper):

    def __init__(self, rows: int = 50, cols: int = 80, mine_spawn: float = 0.15, win_height: int = WIN_HEIGHT, win_title: str = 'Minesweeper 💣🧹', color_mappings: dict = None):
        super().__init__(rows, cols, mine_spawn, win_height, win_title, color_mappings)
