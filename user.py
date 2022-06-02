from game import Minesweeper
from random import randint


SPACER = 50  # amount of lines to print to space boards out
CHOICES = ['r', 'f', 'm', 'q']  # the available menu options
END_CHOICES = ['p', 'e', 'q']  # the available end game options
DEFAULT_MINE_CHANCE = .2 # default mine probability


class User(Minesweeper):

    def __init__(self, rows: int, cols: int, mine_spawn: float, chars_config: dict = None):
        super().__init__(rows, cols, mine_spawn, chars_config)

    def play(self):
        """ Starts game by running start and update function (remember Unity). """
        if self.start() == 'q':  # exits game if quit is entered
            return
        if self.update() == 'q':  # exits game if quit is entered
            return

    def start(self) -> str or None:
        """ Runs startup code for game (first loop of game). """
        space()

        self.display_mask()  # displays game to user
        print('\ninput format: mode row column\nmodes: r | f | m | q')

        # gets menu choice and checks if choice is valid
        mode, choice, last_move = self.check_choice()
        if mode == 'q':
            return 'q'  # exits with "exit code: quit"

        # gets grid coords from input and checks bounds
        mode, row, col = self.check_bounds(mode, choice)
        if mode == 'q':  # breaks outer loop after breaking other loop
            return 'q'  # exits with "exit code: quit"

        self.find_empty_drop(row, col)  # regen board until there's a zero under choice
        self.reveal(row, col)  # reveals spot once the 0 is found
        space()

        return None

    def update(self):
        """ Starts game loop. """
        while True:
            # catches all errors and logs them to error.txt so game doesn't crash
            try:
                # prints last move, mask, and input guide
                print(f'last move: {last_move}\n')
                self.display_mask()  # displays game to user
                print('\ninput format: mode row column\nmodes: r | f | m | q')

                # gets menu choice and checks if choice is valid
                mode, choice, last_move = self.check_choice()
                if mode == 'q':
                    return 'q'  # exits with "exit code: quit"

                print()
                # gets grid coords from input and checks bounds
                mode, row, col = self.check_bounds(mode, choice)
                if mode == 'q':  # breaks outer loop after breaking other loop
                    return 'q'  # exits with "exit code: quit"

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
                            # TODO: Need to add empty spot checker before replay options too!
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
                    error_file.write('LINE NUMBER: ' + str(e.__traceback__.tb_lineno))
                    error_file.write(f'\n{str(e)}\n')
                print('~~ error logged to file ~~')

    def check_inputs(self) :
        """ Runs check_choice() and pipes into check_bounds(). """

    def check_choice(self) -> tuple[str, str, str]:
        """ Gets menu choice input and loops until choice is valid. """
        choice_str = input('\n')
        choice = choice_str.split()
        mode = choice.pop(0).lower()

        while mode not in CHOICES:  # loop if menu choice is invalid
            print('\n choice doesn\'t exist, only: r | f | m | q')
            choice_str = input('\n')
            choice = choice_str.split()
            mode = choice.pop(0).lower()

        return mode, choice, choice_str  # returns unchanged if input was already valid

    def check_bounds(self, mode: str, choice: str) -> tuple[str, int, int]:
        """ Loops until coordinate choice has been made within bounds. """
        row, col = map(int, choice)
        row -= 1  # grid guide is 1-indexed for user, so bring it down
        col -= 1

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

    def find_empty_drop(self, row, col):
        """ Regenerates game board until empty spot is found. """
        while not self.empty_spot(row, col):
            self.regen_game()

    def empty_spot(self, row, col):
        """ Checks if given coords is an empty tile (0) or not. """
        return self.game[row][col] == 0

    def losing_choice(self, ):
        """ Runs losing procedure (triggered when mine is hit). """
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
            rows, cols, prob = get_options()
            self.set_up_game(rows, cols, prob)
        elif end_choice == 'q':  # quits game
            return 'q'


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
