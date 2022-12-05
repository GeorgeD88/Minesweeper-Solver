# interface
import pygame
import ptext
from gui_colors import *
from constants import *

# data structures
from collections import deque

# dev stuff
from pprint import PrettyPrinter
from typing import Generator

# miscellaneous
import random

""" The input sanitization will be kept to a minimum or likely none, because remember
this is just the backend mechanics, these are the strings of a piano that do shit.
The backend is simply the gears that do shit, they aren't expected to handle
odd instructions and shit, that's the job of the frontend that feeds to the backend. """

pp = PrettyPrinter().pprint  # for dev purposes

class Node:

    def __init__(self, visualizer, row: int, col: int, value: bool or int):
        self.parent = visualizer  # visualizer class that holds these nodes
        self.size = visualizer.cell_size  # side length of the cell

        self.x, self.y = col * self.size, row * self.size  # pixel coord in the pygame window
        self.row, self.col = row, col  # coord of node on the board

        self.state = self.parent.UNREVEALED  # current state/color of the node
        self.value = value  # minesweeper tile value (0 to 9 or mine)

    def get_coord(self) -> tuple[int, int]:
        """ Returns node's coordinate. """
        return (self.row, self.col)

    # FIXME: trying to decide if this should automatically reveal to mine
    def reveal(self):
        """ Set node state to revealed, or to mine if its value is a mine. """
        self.state = self.parent.REVEALED if self.value is not True else self.parent.MINE

    def unreveal(self):
        """ Set node state to unrevealed. """
        self.state = self.parent.UNREVEALED

    def is_unrevealed(self) -> bool:
        """ Returns whether node is unrevealed. """
        return self.state == self.parent.UNREVEALED

    # NOTE: to check if node is unrevealed OR flagged, do !is_revealed()
    def is_revealed(self) -> bool:
        """ Returns whether node is revealed. """
        return self.state == self.parent.REVEALED

    def is_mine(self) -> bool:
        """ Returns whether node is a mine. """
        return self.value is True

    def is_flagged(self) -> bool:
        """ Returns whether node is flagged. """
        return self.state == self.parent.FLAG

    def flag(self) -> bool:
        """ Flags node. """
        self.state = self.parent.FLAG

    def is_empty(self) -> bool:
        """ Returns whether node is an empty area (zero). """
        return self.value == 0


class Minesweeper:
    """ Game logic + visual (graphical), NOT INPUT. From here, we add the user input through a subclass (in another file) to play the game. """

    def __init__(self, rows: int = 25, cols: int = 40, mine_spawn: float = 0.15, win_height: int = WIN_HEIGHT, win_title: str = 'Minesweeper 💣🧹', color_mappings: dict = None):
        # pygame window dimensions
        self.win_height = win_height  # window height
        self.cell_size = self.win_height // rows  # visual cell size
        self.cell_grid_size = self.cell_size * 0.56  # actual grid length (aesthetic purposes)
        self.grid_space = (self.cell_size - self.cell_grid_size) // 2  # the empty spaces in grid sides
        self.win_width = self.cell_size * cols  # window width

        # pygame window (everything is drawn here)
        self.win = pygame.display.set_mode((self.win_width, self.win_height))
        pygame.display.set_caption(win_title)
        # self.mine_icon = pygame.image.load('mine-icon.png')

        # sets each color mapping to default value if custom color aren't provided
        if color_mappings is None:
            self.GRID_LINE = GRAY
            self.TILE_NUMBER = WHITE  # tile foreground color (tile number)
            self.REVEALED = DARK_GRAY  # tile background color (behind number)
            self.LOSS_REVEALED = DARK_GRAY_LOSS  # tile background color (behind number)
            self.UNREVEALED = PURPLE  # color theme
            self.MINE = RED
            self.WIN_MINE = GREEN
            self.FLAG = GRAY_BLUE#LIGHT_GRAY#SOFT_BLUE
        # else color mappings were provided so sets values of provided colors
        else:
            self.GRID_LINE = GRAY if 'GRID_LINE' not in color_mappings else color_mappings['GRID_LINE']
            self.TILE_NUMBER = WHITE if 'TILE_NUMBER' not in color_mappings else color_mappings['TILE_NUMBER']
            self.REVEALED = DARK_GRAY if 'REVEALED' not in color_mappings else color_mappings['REVEALED']
            self.LOSS_REVEALED = DARK_GRAY_LOSS if 'LOSS_REVEALED' not in color_mappings else color_mappings['LOSS_REVEALED']
            self.UNREVEALED = PURPLE if 'UNREVEALED' not in color_mappings else color_mappings['UNREVEALED']
            self.MINE = RED if 'MINE' not in color_mappings else color_mappings['MINE']
            self.WIN_MINE = GREEN if 'WIN_MINE' not in color_mappings else color_mappings['WIN_MINE']
            self.FLAG = GRAY_BLUE if 'FLAG' not in color_mappings else color_mappings['FLAG']

        # board properties
        self.rows, self.cols = rows, cols  # board dimensions
        self.area = rows * cols  # number of total tiles
        self.mine_spawn = mine_spawn  # probability of mine spawn

        # game setup
        self.revealed_count = 0  # keeps track of how many tiles were revealed (not flagged)
        # mine count is initialized in self.generate_mine_matrix()
        self.initialize_board()
        self.draw()

    # === GAME SETUP FUNCTIONS ===
    def generate_mine_matrix(self) -> list[list]:
        """ Generates a matrix of mines (booleans) based on game's mine spawn probability. """
        # generate mine matrix by probability
        if self.mine_spawn < 1:
            mine_board = []
            self.mine_count = 0  # stores total number of mines
            for _ in range(self.rows):
                mine_board.append([])  # append new row list
                for _ in range(self.cols):
                    # randomly generates mine
                    if random.random() < self.mine_spawn:
                        mine_board[-1].append(True)
                        self.mine_count += 1
                    else:
                        mine_board[-1].append(False)
        # generate mine matrix by mine count
        else:
            mine_board = [[False]*self.cols for _ in range(self.rows)]
            self.mine_count = self.mine_spawn
            # generates random mine coord for the number of desired mines
            for _ in range(self.mine_spawn):
                # generate random coord until you get a coord with no mine already
                while True:
                    rr, cc = random.randrange(self.rows), random.randrange(self.cols)
                    if mine_board[rr][cc] is False:
                        mine_board[rr][cc] = True
                        break

        return mine_board

    def count_adjacent_mines(self):
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
        self.revealed_count = 0

        # traverse board and set values according to new mines
        for r in range(self.rows):
            for c in range(self.cols):
                self.get_node(r, c).unreveal()
                self.get_node(r, c).value = True if mines[r][c] is True else 0

        # traverse board and count mines
        self.count_adjacent_mines()

    def reset_game(self):
        """ Sets all tiles back to unrevealed but doesn't regenerate game board values. """
        self.revealed_count = 0
        for r in range(self.rows):
            for c in range(self.cols):
                self.get_node(r, c).unreveal()

    def generate_empty_drop(self, node: Node):
        """ Regenerates board until given node is an empty spot. """
        while not node.is_empty():
            self.new_game()

    # === HELPER FUNCTIONS ===
    def gen_matrix(self, default=None) -> list[list]:
        """ Generates a 2D array the size of the board consisting of the given default value. """
        nested_arr = [] if default is None else [default]*self.cols
        return [nested_arr for _ in range(self.rows)]

    def get_node(self, r: int, c: int) -> Node:
        """ Returns the node at the given coord. """
        return self.board[r][c]

    def adjacent_coords(self, r: int, c: int) -> Generator[tuple[int, int], None, None]:
        """ Returns the coords adjacent to the given coord. """
        for offset in ADJACENT_COORDS:
            adj_coord = self.offset_coord((r, c), offset)
            if self.bounds(*adj_coord) is True:
                yield adj_coord

    def adjacent_nodes(self, node: Node) -> Generator[Node, None, None]:
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
        return self.area - self.revealed_count == self.mine_count

    def is_loss(self, node: Node) -> bool:
        """ Checks if coord choice is a loss (mine). """
        # NOTE: I should remove the is new and have that checked externally, because really the input should be sanitized before.
        return node.state == self.UNREVEALED and node.value is True

    # === PYGAME FUNCTIONS ===
    def update_display(self):
        """ Simple wrapper for pygame.display.update() function. """
        pygame.display.update()

    def draw_flag(self, node: Node):
        """ Draws tile with flag emoji onto pygame window. """
        ptext.draw(FLAG_STR, centerx=node.x+self.cell_size//2, centery=node.y+self.cell_size//2, fontsize=int(self.cell_size/4*3))#3:2

    def draw_number(self, node: Node):
        """ Draws node's number onto pygame window. """
        ptext.draw(str(node.value), centerx=node.x+self.cell_size//2, centery=node.y+self.cell_size//2, fontsize=int(self.cell_size/4*3))#3:2

    def draw_mine(self, node: Node):
        """ Draws node's mine symbol onto pygame window. """
        ptext.draw('X', centerx=node.x+self.cell_size//2, centery=node.y+self.cell_size//2, fontsize=int(self.cell_size/4*3))#3:2

    def draw_node(self, node: Node):
        """ Draws given node onto pygame window. """
        pygame.draw.rect(self.win, node.state, (node.x, node.y, self.cell_size, self.cell_size))

    def draw_node_grid(self, node: Node):
        """ Draws given node's grid lines onto pygame window. """
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

    # just drawing functions ==
    # NOTE: WE ARE USING THIS FOR DRAWING FLAGS TOO, DON'T FORGET !!
    def draw_unrevealed(self, node: Node):
        """ Draws unrevealed node. """
        self.draw_node(node)
        if node.is_flagged():
            self.draw_flag(node)
            self.draw_node_grid(node)

    def draw_revealed(self, node: Node):
        """ Draws revealed node. """
        self.draw_node(node)  # draws tile color, aka bg
        self.draw_node_grid(node)  # draws grid lines
        if not node.is_empty():  # draws number if value over 0
            if node.is_mine():
                self.draw_mine(node)
            else:
                self.draw_number(node)  # draws tile number, aka fg

    """ NOTE: we're drawing mines with revealed nodes, just keep that in mind
    incase there are errors in the future and you might want to separate them. """

    # wrap drawing functions w/ display updating too ==
    def update_unrevealed(self, node: Node):
        """ Draws unrevealed node and updates display. """
        self.draw_unrevealed(node)
        self.update_display()

    def update_revealed(self, node: Node):
        """ Draws revealed node and updates display. """
        self.draw_revealed(node)
        self.update_display()

    def update_node(self, node: Node):
        """ Draws unrevealed/revealed node and updates display. """
        if node.is_revealed():
            self.draw_revealed(node)  # directly using the draw functions
        else:  # this will run for flags and specifically unrevealed
            self.draw_unrevealed(node)
        self.update_display()  # and updating here. instead of just running the update functions

    # wrap drawing revealed w/ reveal, no updating ==
    # NOTE: this is for floodfills where I want to reveal and draw a group of nodes, then display the group together
    def reveal_node(self, node: Node):
        """ Reveals and draws node without updating, and increments revealed counter. """
        node.reveal()  # reveals node
        self.draw_revealed(node)  # draws node onto window
        self.revealed_count += 1  # increments revealed counter

    def draw(self):
        """ Draws the whole board then updates display. """
        # fill window with white
        self.win.fill(WHITE)

        # goes through every node in the grid and draws it
        for row in self.board:
            for node in row:
                self.draw_node(node)
                if node.is_revealed():  # only draws grid for revealed nodes
                    self.draw_node_grid(node)

        self.update_display()

    # === GAME FUNCTIONS ===
    def flag(self, node: Node):
        """ Flags node, or unflags if node was already flagged. """
        if node.is_flagged():  # unflag if node is already flagged
            node.unreveal()
        else:  # node is unrevealed, flag it
            node.flag()
        self.update_node(node)  # draws node and updates display

    def reveal(self, node: Node):
        """ Reveals given node and flood fills area if needed. """
        # flood fill if revealed node is empty (zero)
        if node.value == 0:
            # NOTE: to change the type of flood fill you use, change this function
            self.level_order_floodfill(node)
        else:
            # NOTE: IMPORTANT TO USE THIS SPECIFIC REVEAL FUNCTION AS IT INCREMENTS REVEALED COUNTER TOO
            self.reveal_node(node)  # reveals and draws node
            self.update_display()  # updates revealed node

    # NOTE: helper function for chording, will also be used for solver
    def count_flags(self, node: Node):
        """ Counts number of adjacent flags. """
        flag_count = 0
        for adj in self.adjacent_nodes(node):
            if adj.is_flagged():
                flag_count += 1
        return flag_count

    def chord(self, node: Node):
        """ Chords given node. """
        flag_count = 0
        # counts flags and checks for incorrect placement as it counts
        for adj in self.adjacent_nodes(node):
            if adj.is_flagged():
                if not adj.is_mine():  # incorrect flag, exits function
                    return False
                flag_count += 1

        # if flags are correct, reveals all unrevealed tiles
        if flag_count == node.value:
            for adj in self.adjacent_nodes(node):
                if adj.is_unrevealed():  # specifically unrevealed, not also flagged
                    self.reveal(adj)  # reveals and draws node

        # updates all newly drawn nodes at once
        self.update_display()

    # flood fill algorithms ==
    def level_order_floodfill(self, start: Node):
        """ Flood fills board using level order traversal starting at given node """
        queue = deque([start])  # append to enqueue and popleft to dequeue
        discovered = {start}  # hashset keeping track of already discovered nodes

        while len(queue) > 0:
            breadth = len(queue)  # get length of current breadth of nodes

            # iterate breadth of nodes
            for _ in range(breadth):
                curr = queue.popleft()  # pop node to process

                # process node
                self.reveal_node(curr)  # reveal and draw node (doesn't update) also increments revealed counter
                if curr.value != 0:  # stops traversing this point if it hits edge of empty pool
                    continue         # empty pool is contained by edge of number tiles (above 0)

                # add adjacent nodes
                for adj in self.adjacent_nodes(curr):
                    # NOTE: if node isn't new then it was processed during a different run of this function.
                    if adj not in discovered and adj.is_unrevealed():
                        discovered.add(adj)
                        queue.append(adj)

            # displays whole breadth of newly drawn nodes together
            self.delay()
            self.update_display()

    def level_order_loss(self, start: Node):
        """ Traverses the whole board and reveals everything, loss procedure.
        NOTE: If the way I implemented any of this confuses you, the reason for all of it is that the animation
        should be a level order traversal across the whole board, ignoring any already revealed tiles and
        traversing across them as if they don't exist, and revealing everything in its path, even mines. """

        queue = deque([start])  # append to enqueue and popleft to dequeue
        discovered = {start}  # hashset keeping track of already discovered nodes

        while len(queue) > 0:
            breadth = len(queue)  # get length of current breadth of nodes

            # iterate breadth of nodes
            for _ in range(breadth):
                curr = queue.popleft()  # pop node to process

                # process node
                if curr.is_unrevealed() and not curr.is_flagged():  # ignores already revealed or flagged tiles
                    # reveal (modified reveal)
                    curr.state = self.LOSS_REVEALED if curr.value is not True else self.MINE
                    self.draw_revealed(curr)

                # add adjacent nodes
                for adj in self.adjacent_nodes(curr):
                    if adj not in discovered:
                        discovered.add(adj)
                        queue.append(adj)

            # displays whole breadth of newly drawn nodes together
            self.delay()
            self.update_display()

    def level_order_win(self, start: Node):
        """ Traverses the whole board and recolors all mines, win procedure. """
        queue = deque([start])  # append to enqueue and popleft to dequeue
        discovered = {start}  # hashset keeping track of already discovered nodes

        while len(queue) > 0:
            breadth = len(queue)  # get length of current breadth of nodes

            # iterate breadth of nodes
            for _ in range(breadth):
                curr = queue.popleft()  # pop node to process

                # process node
                if curr.is_mine():
                    # reveal (modified reveal)
                    curr.state = self.WIN_MINE
                    self.draw_revealed(curr)

                # add adjacent nodes
                for adj in self.adjacent_nodes(curr):
                    if adj not in discovered:
                        discovered.add(adj)
                        queue.append(adj)

            # displays whole breadth of newly drawn nodes together
            self.delay()
            self.update_display()
