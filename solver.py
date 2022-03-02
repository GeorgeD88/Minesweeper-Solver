from game import Minesweeper
from random import randint
from time import sleep

SPACER = 50  # amount of lines to print to space boards out
# CHOICES = ['r', 'f', 'm', 'q']  # the available menu options
# END_CHOICES = ['p', 'e', 'q']  # the available end game options
# FIXME: might need to do file for solver display, and then file for solver algorithms.
#        cause unlike user, solver is display + other backend.

# NOTE: remember to only give the bot access to what a regular player could see to make it accurate.
class Solver(Minesweeper):

    def __init__(self, rows: int, cols: int, mine_spawn: float, chars_config: dict = None):
        super().__init__(rows, cols, mine_spawn, chars_config)

    def visualizer(self):
        """ Starts game/solving loop. """
        # last_move = ''
        space()

        while True:

            # catches all errors and logs them to error.txt so game doesn't crash
            try:
                # prints last move, mask, and input guide
                print(f'last move: {last_move}\n')
                self.display_mask()  # displays game to user
                print('\ninput format: mode row column\nmodes: r | f | m | q')

                # gets input
                choice_str = last_move = input('\n')
                choice = choice_str.split()
                mode = choice.pop(0).lower()
                # keeps looping until proper menu choice
                while mode not in CHOICES:
                    print('\n choice doesn\'t exist, only: r | f | m | q')
                    choice_str = last_move = input('\n')
                    choice = choice_str.split()
                    mode = choice.pop(0).lower()
                if mode == 'q':
                    break
                row, col = map(int, choice)
                row -= 1
                col -= 1
                print()

                # input checking to ensure it's within bounds
                while not self.bounds(row, col):
                    print('selection out of bounds\n')
                    choice = input('\n').split()
                    mode = choice.pop(0).lower()
                    if mode == 'q':
                        break
                    row, col = map(int, choice)
                    row -= 1
                    col -= 1
                    print()

                # if Q is selected in redo loop, it wil break there so this is to break outer loop
                if mode == 'q':
                    break

                # executes choices: r | f | m | q
                if mode == 'r':
                    # checks if choice was a mine (and mask is unexplored) and ends game
                    if self.mask[row][col] is False and self.game[row][col] is True:
                        space()
                        self.display_game(border=True)
                        lose_message()
                        end_choice = input().lower()
                        # keeps looping until proper end game choice
                        while end_choice not in END_CHOICES:
                            print('\n choice doesn\'t exist, only: P | E | Q')
                            end_choice = input().lower()
                        if end_choice == 'p':  # play again
                            self.reset_game()
                        elif end_choice == 'e':  # edit settings
                            print()
                            last_move = ''
                            rows, cols, prob = get_options()
                            self.set_up_game(rows, cols, prob)
                        elif end_choice == 'q':  # quits game
                            break
                    # if no mine then continue with revealing square
                    else:
                        self.reveal(row, col)
                        if self.iswin():  # if there's nothing more to be explored, it's a win
                            space()
                            self.display_game(border=True)
                            win_message()
                            end_choice = input().lower()
                            # keeps looping until proper end game choice
                            while end_choice not in END_CHOICES:
                                print('\n choice doesn\'t exist, only: P | E | Q')
                                end_choice = input().lower()
                            if end_choice == 'p':  # play again
                                self.reset_game()
                            elif end_choice == 'e':  # edit settings
                                print()
                                last_move = ''
                                rows, cols, prob = get_options()
                                self.set_up_game(rows, cols, prob)
                            elif end_choice == 'q':  # quits game
                                break
                elif mode == 'f':
                    self.flag(row, col)
                elif mode == 'm':
                    self.maybe(row, col)
                space()

            except Exception as e:
                with open('error.txt', 'w+') as error_file:
                    error_file.write('LINE NUMBER: ' + str(e.__traceback__.tb_lineno))
                    error_file.write('\n' + str(e))
                print('~~ error logged to file ~~')

    def random_drop(self):
        """ Randomly picks coord to drop onto. """
        self.reveal(randint(0, self.rows-1), randint(0, self.cols-1))

    def persistent_drop(self):
        """ Keeps dropping until it hits a zero. """
        row, col = randint(0, self.rows-1), randint(0, self.cols-1)
        self.reveal(row, col)
        while self.mask[row][col] != 0:  # keep going while you're not getting zero
            row, col = randint(0, self.rows-1), randint(0, self.cols-1)
            self.reveal(row, col)


def get_options():
    """ Gets game options: rows, columns, and mine probability. """
    options_input = input('format: rows  columns  probability(optional)\n').split()
    return int(options_input[0]), int(options_input[1]), float(options_input[2])

def space():
    print('\n'*SPACER)

def welcome_message():
    print("""


               ====================================
               === WELCOME TO MINESWEEPER! 💣🧹 ===
               ====================================

                    To get started, input your
             desired dimensions and mine probability.

            """)

def win_message():
    print("""


               ===============
               == YOU WIN!! ==
               ===============

  (P) play again (Q) quit (E) edit settings
            """)

def lose_message():
    print("""


               ===============
               == GAME OVER ==
               ===============

  (P) play again (Q) quit (E) edit settings
            """)

def init_solver():
    welcome_message()
    print('           ', end='')  # prints a spacer to push get options message under welcome message
    rows, cols, prob = get_options()
    return Solver(rows, cols, prob)