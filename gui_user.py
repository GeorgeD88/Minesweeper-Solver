# interface
import pygame
from gui_minesweeper import Minesweeper, Node
from constants import *

# data structures
from collections import deque

# dev stuff
from pprint import PrettyPrinter


pp = PrettyPrinter().pprint  # for dev purposes


class User(Minesweeper):

    def __init__(self, rows: int = ROWS, cols: int = COLS, mine_spawn: float = MINE_SPAWN, win_height: int = WIN_HEIGHT, win_title: str = WIN_TITLE, color_mappings: dict = None):
        super().__init__(rows, cols, mine_spawn, win_height, win_title, color_mappings)
        # pygame.event.set_blocked(pygame.MOUSEMOTION)

    def get_clicked_coord(self, pos):
        """ Gets the coord of node clicked based on position clicked in window. """
        x, y = pos

        # divides window position by cell width to see row/col number
        row = y // self.cell_size
        col = x // self.cell_size

        return row, col

    def get_clicked_node(self, pos):
        """ Gets the node clicked based on position in window clicked. """
        return self.get_node(*self.get_clicked_coord(pos))

    def count_flags(self, node: Node):
        """ Counts number of adjacent flags. """
        flag_count = 0

        for adj in self.adjacent_nodes(node):
            if adj.is_flagged():
                flag_count += 1

        return flag_count

        # flag count matches mine count, reveal surrounding unrevealed nodes


    def chord(self, node: Node):
        """ Chords given node. """
        if self.count_flags(node) == node.value:
            for adj in self.adjacent_nodes(node):
                if adj == self.UNREVEALED:
                    adj.reveal()

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
                    pos = pygame.mouse.get_pos()
                    node = self.get_clicked_node(pos)

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

                # left click, reveal tile
                if pygame.mouse.get_pressed()[0]:
                    # get position on window clicked and then get node at position
                    pos = pygame.mouse.get_pos()
                    node = self.get_clicked_node(pos)

                    if node.is_revealed():  # can't reveal already revealed node
                        self.chord(node)
                    elif node.is_flagged():
                        continue
                    elif node.is_mine():  # run lose procedure if node is a mine
                        lose_message()
                        input()
                        exit()
                    else:  # node is safe, reveal it
                        self.reveal(node)
                        if self.is_win():
                            win_message()
                            input()
                            exit()

                # right click, flag tile
                elif pygame.mouse.get_pressed()[2]:
                    # get position on window clicked and then get node at position
                    pos = pygame.mouse.get_pos()
                    node = self.get_clicked_node(pos)

                    if node.is_revealed():  # can't flag revealed node
                        continue
                    else:  # toggle flog
                        self.flag(node)

                # key press
                if event.type == pygame.KEYDOWN:
                    # R, resets game but keeps same board
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.draw()

                    # N, starts new game so board is wiped
                    elif event.key == pygame.K_n:
                        self.new_game()
                        self.draw()

                    # S, run solver
                    elif event.key == pygame.K_s:
                        pass

                    # else, some other key was pressed

        pygame.quit()


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


def main():
    # TODO: make different size presets
    ms = User()
    ms.play()


if __name__ == "__main__":
    main()
