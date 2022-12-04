# interface
import pygame
from gui_game import Minesweeper, Node
from constants import *

# data structures
from collections import deque

# dev stuff
from pprint import PrettyPrinter


pp = PrettyPrinter().pprint  # for dev purposes


class User(Minesweeper):

    def __init__(self, rows: int = ROWS, cols: int = COLS, mine_spawn: float or int = MINE_SPAWN, win_height: int = WIN_HEIGHT, win_title: str = WIN_TITLE, color_mappings: dict = None):
        super().__init__(rows, cols, mine_spawn, win_height, win_title, color_mappings)
        pygame.event.set_blocked(pygame.MOUSEMOTION)

    def coord_from_pos(self, pos):
        """ Gets the grid coord of node clicked based on position clicked in window. """
        x, y = pos

        # divides window position by cell width to see row/col number
        row = y // self.cell_size
        col = x // self.cell_size

        return row, col

    def get_clicked_node(self):
        """ Gets the node clicked based on position in window clicked. """
        pos = pygame.mouse.get_pos()  # get mouse position
        coord = self.coord_from_pos(pos)  # convert position to coord
        return self.get_node(*coord)  # get node at coord

    # === MAIN ===
    def play(self):
        """ Starts game by running start and update function (remember Unity). """
        self.start()
        self.update()

    def start(self):
        """ Runs startup code for game (first loop of game) all this is needed just so I can do an empty drop, bruh. """
        self.draw()  # displays initial board
        running = True

        while running:
            # MOUSEMOTION event is important because it allows you to hold down and place

            for event in pygame.event.get():

                # window exit button
                if event.type == pygame.QUIT:
                    running = False
                    break  # breaks event loop, not main loop

                # left click, reveal tile
                if pygame.mouse.get_pressed()[0]:
                    # get position on window clicked and then get node at position
                    node = self.get_clicked_node()

                    self.generate_empty_drop(node)  # regen board until there's a zero under choice
                    self.reveal(node)  # reveals spot once the 0 is found
                    return

        pygame.quit()

    def update(self):
        """ Main function. """

        # main update loop
        running = True
        while running:
            # MOUSEMOTION event is important because it allows you to hold down and place

            for event in pygame.event.get():

                # window exit button
                if event.type == pygame.QUIT:
                    running = False
                    break  # breaks event loop, not main loop

                # mouse click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # left click, reveal tile
                    if event.button == 1:#pygame.mouse.get_pressed()[0]:
                        # get position on window clicked and then get node at position
                        node = self.get_clicked_node()

                        # sanitize input before trying to reveal
                        if node.is_revealed() and not node.is_empty():  # chord node
                            # chord returns false if you incorrectly flagged
                            if self.chord(node) is False:
                                self.level_order_loss(node)
                        elif node.is_flagged():  # can't reveal flagged node
                            continue
                        elif node.is_mine():  # run lose procedure if node is a mine
                            node.reveal()  # reveal node (mine), without incrementing revealed count
                            self.update_revealed(node)  # update revealed mine
                            self.level_order_loss(node)
                        else:  # node is safe, reveal it
                            self.reveal(node)
                            if self.is_win():
                                self.level_order_win(node)

                    # right click, flag tile
                    elif event.button == 3:#pygame.mouse.get_pressed()[2]:
                        # get position on window clicked and then get node at position
                        node = self.get_clicked_node()

                        # sanitize input before trying to flag
                        if node.is_revealed():  # can't flag revealed node
                            continue
                        else:  # as long as it's not revealed, then run flag()
                            self.flag(node)  # toggle flag

                # key press
                elif event.type == pygame.KEYDOWN:
                    # R, resets game but keeps same board
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.draw()

                    # N, starts new game so board is wiped
                    elif event.key == pygame.K_n:
                        self.new_game()
                        self.start()

                    # S, run solver
                    elif event.key == pygame.K_s:
                        pass

                    # else, some other key was pressed

        pygame.quit()

def end_procedure(end_message):
    end_message()
    input()
    # TODO: need to make it where it just exits the input loop and you can only exit
    exit()

def win_message():
    print("""


               ===============
               == YOU WIN!! ==
               ===============

""")

def lose_message():
    print("""


               ===============
               == GAME OVER ==
               ===============

""")