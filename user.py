from game import Minesweeper
from random import randint


SPACER = 50  # amount of lines to print to space boards out
CHOICES = ['r', 'f', 'm', 'q']  # the available menu options
END_CHOICES = ['p', 'e', 'q']  # the available end game options
DEFAULT_MINE_CHANCE = .18  # default mine probability


class User(Minesweeper):

    def __init__(self, rows: int, cols: int, mine_spawn: float, chars_config: dict = None):
        super().__init__(rows, cols, mine_spawn, chars_config)

    def play(self):
        """ Starts game loop. """
        last_move = ''
        space()

        # regen board until there's a zero at choice

        while True:

            # catches all errors and logs them to error.txt so game doesn't crash
            try:
                # prints last move, mask, and input guide
                print(f'last move: {last_move}\n')
                self.display_mask()  # displays game to user
                print('\ninput format: mode row column\nmodes: r | f | m | q')

                # gets menu choice
                choice_str = last_move = input('\n')
                choice = choice_str.split()
                mode = choice.pop(0).lower()
                # then pipes menu choice through checker
                mode, choice_str = self.check_choice(mode, choice_str)
                if mode == 'q':
                    break

                # gets grid coords from input
                row, col = map(int, choice)
                row -= 1  # grid guide is 1-indexed for user, so bring it down
                col -= 1
                print()
                # then pipe coords through bounds checker
                mode, row, col = self.check_bounds(mode, row, col)
                if mode == 'q':  # breaks outer loop after breaking other loop
                    break

                # executes choices: r | f | m | q
                if mode == 'r':
                    # checks if choice was a mine (and mask is unexplored) and ends game
                    if self.mask[row][col] is False and self.game[row][col] is True:
                        space()
                        self.display_game(border=True)
                        lose_message()
                        replay_options()
                        end_choice = input().lower()
                        # keeps looping until proper end game choice
                        while end_choice not in END_CHOICES:
                            print('\n choice doesn\'t exist, only: P | E | Q')
                            end_choice = input().lower()
                        if end_choice == 'p':  # play again
                            self.regen_game()
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
                            replay_options()
                            end_choice = input().lower()
                            # keeps looping until proper end game choice
                            while end_choice not in END_CHOICES:
                                print('\n choice doesn\'t exist, only: P | E | Q')
                                end_choice = input().lower()
                            if end_choice == 'p':  # play again
                                self.regen_game()
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
                with open('user_error_log.txt', 'a+') as error_file:
                    error_file.write('LINE NUMBER: ' +
                                     str(e.__traceback__.tb_lineno))
                    error_file.write(f'\n{str(e)}\n')
                print('~~ error logged to file ~~')

    def check_choice(self, mode: str, choice_str: str) -> tuple[str, str]:
        """ Loops until menu choice input has been made. """
        while mode not in CHOICES:  # loop if menu choice is invalid
            print('\n choice doesn\'t exist, only: r | f | m | q')
            choice_str = input('\n')
            choice = choice_str.split()
            mode = choice.pop(0).lower()

        return (mode, choice_str)  # returns unchanged if input was already valid

    def check_bounds(self, mode: str, row: int, col: int) -> tuple[str, int, int]:
        """ Loops until coordinate choice has been made within bounds. """
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

        return mode, row, col  # returns unchanged if coords were already within bounds


def get_options():
    """ Gets game options: rows, columns, and mine probability. """
    options_input = input(
        'format: rows  columns  probability(optional)\n').split()
    # use default probability if it wasn't given
    probability = DEFAULT_MINE_CHANCE if len(
        options_input) < 3 else float(options_input[2])
    return int(options_input[0]), int(options_input[1]), probability


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
            """)


def lose_message():
    print("""


               ===============
               == GAME OVER ==
               ===============
            """)


def replay_options():
    print("""
  (P) play again (Q) quit (E) edit settings
            """)


def init_game():
    welcome_message()
    # prints a spacer to push get options message under welcome message
    print('           ', end='')
    rows, cols, prob = get_options()
    return User(rows, cols, prob)
