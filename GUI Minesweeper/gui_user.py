# interface
import pygame
from gui_solver import Solver
from gui_colors import *
from constants import *

# dev stuff
from pprint import PrettyPrinter


pp = PrettyPrinter().pprint  # for dev purposes


class User(Solver):
    """ The same thing as subclassing from Minesweeper, except the Solver file is a middleman
    to add all the solver code in between, while still keeping the final input loop separate. """

    def __init__(self, rows: int = ROWS, cols: int = COLS, mine_spawn: float or int = MINE_SPAWN, win_height: int = WIN_HEIGHT, win_title: str = WIN_TITLE):
        super().__init__(rows, cols, mine_spawn, win_height, win_title)
        pygame.event.set_blocked(pygame.MOUSEMOTION)

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

            for event in pygame.event.get():

                # window exit button
                if event.type == pygame.QUIT:
                    running = False
                    break  # breaks event loop, not main loop

                # left click, reveal tile
                # if pygame.mouse.get_pressed()[0]:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # get position on window clicked and then get node at position
                    node = self.get_clicked_node()
                    self.first_drop = node.get_coord()  # save this coord as the first drop coord

                    self.generate_empty_drop(node)  # regen board until there's a zero under choice
                    self.reveal(node)  # reveals spot once the 0 is found
                    return

        pygame.quit()

    def update(self):
        """ Main function. """

        # main update loop
        running = True
        while running:

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
                        if node.state == self.LAKE:  # do nothing
                            pass
                        elif self.is_revealed_solver(node) and not node.is_empty():  # chord node
                            # chord returns false if you incorrectly flagged
                            chord_result = self.chord(node)
                            # lose if chord is wrong (flags were wrong)
                            if chord_result is False:
                                self.level_order_loss(node)
                                pygame.event.clear()  # ignore events added during animation
                            # check if chord resulted in a win
                            elif self.is_win():
                                self.level_order_win(node)
                                pygame.event.clear()  # ignore events added during animation
                        elif node.is_flagged():  # can't reveal flagged node
                            continue
                        elif node.is_mine():  # run lose procedure if node is a mine
                            node.reveal()  # reveal node (mine), without incrementing revealed count
                            self.update_revealed(node)  # update revealed mine
                            self.level_order_loss(node)
                        else:  # node is safe, reveal it
                            # avoids increasing revealed counter for already revealed by solver
                            if node.state in self.revealed_states:
                                continue
                            else:
                                self.reveal(node)
                                if self.is_win():
                                    self.level_order_win(node)
                                    pygame.event.clear()  # ignore events added during animation

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
                        self.solve_board()
                        # clear event queue after solving, this ignores buttons pressed during solve cycle
                        pygame.event.clear()

                        if self.is_win():
                            self.level_order_win(self.get_node(*self.first_drop))

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
