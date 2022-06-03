from game import Minesweeper
from random import randint
import math


SPACER = 50  # amount of lines to print to space boards out
CHOICES = ['r', 'f', 'm', 'q']  # the available menu options
END_CHOICES = ['p', 'e', 'q']  # the available end game options
REPLAY_MENU = '(P) play again (Q) quit (E) edit settings'
DEFAULT_MINE_CHANCE = .2 # default mine probability


class User(Minesweeper):

    def __init__(self, rows: int, cols: int, mine_spawn: float, chars_config: dict = None):
        super().__init__(rows, cols, mine_spawn, chars_config)

    def play(self):
        """ Starts game by running start and update function (remember Unity). """
        start_resp = self.start()
        if start_resp == 'q':  # exits game if quit is entered
            return
        if self.update(start_resp) == 'q':  # exits game if quit is entered
            return

    def start(self) -> str:
        """ Runs startup code for game (first loop of game). """
        space()

        self.display_mask()  # displays game to user
        print('\ninput format: mode row column\nmodes: r | f | m | q')

        input_check = self.check_inputs()
        if input_check[0] == 'q':  # checks menu choice and coords
            return 'q'
        mode, last_move, row, col = input_check

        self.find_empty_drop(row, col)  # regen board until there's a zero under choice
        self.reveal(row, col)  # reveals spot once the 0 is found
        space()

        return last_move

    def update(self, last_move: str):
        """ Starts game loop. """

        while True:
            # catches all errors and logs them to error.txt so game doesn't crash
            try:
                self.round_print(last_move)  # prints board and such

                input_check = self.check_inputs()
                if input_check[0] == 'q':  # checks menu choice and coords
                    return 'q'
                mode, last_move, row, col = input_check

                # executes choices: r | f | m | q
                if mode == 'r':
                    if self.isloss(row, col):  # checks if coord is bomb
                        if self.losing_procedure() == 'q':
                            return 'q'
                        last_move = self.start()
                        if last_move == 'q':  # exits game if quit is entered
                            return 'q'
                    else:  # if no loss, continues revealing tile regularly
                        self.reveal(row, col)
                        if self.iswin():  # if there's nothing more to be explored, it's a win
                            if self.win_procedure() == 'q':
                                return 'q'
                            last_move = self.start()
                            if last_move == 'q':  # exits game if quit is entered
                                return 'q'
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

    def round_print(self, last_move: str):
        """ Prints the last move, mask, and input guide for the round. """
        print(f'last move: {last_move}\n')
        self.display_mask()  # displays game to user
        print('\ninput format: mode row column\nmodes: r | f | m | q')

    def check_inputs(self) :
        """ Runs check_choice() and pipes into check_bounds(). """
        # gets menu choice and checks if choice is valid
        mode, choice, last_move = self.check_choice()
        if mode == 'q':
            return ('q')  # exits with "exit code: quit"

        print()

        # gets grid coords from input and checks bounds
        mode, row, col = self.check_bounds(mode, choice)
        if mode == 'q':  # breaks outer loop after breaking other loop
            return ('q')  # exits with "exit code: quit"

        return mode, last_move, row, col

    def check_choice(self) -> tuple[str, str, str]:
        """ Gets menu choice input and loops until choice is valid. """
        choice_str = input('\n').strip()
        while choice_str == '':
            print('\n can\'t enter empty input')
            choice_str = input('\n').strip()
        choice = choice_str.split()
        mode = choice.pop(0).lower()

        while mode not in CHOICES:  # loop if menu choice is invalid
            print('\n choice doesn\'t exist, only: r | f | m | q')
            choice_str = input('\n').strip()
            while choice_str == '':
                print('\n can\'t enter empty input')
                choice_str = input('\n').strip()
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
            while choice_str == '':
                print('\n can\'t enter empty input')
                choice_str = input('\n').strip()
            mode = choice.pop(0).lower()
            if mode == 'q':
                break
            row, col = map(int, choice)
            row -= 1
            col -= 1
            print()

        return mode, row, col  # returns unchanged if coords were already within bounds

    def losing_procedure(self):
        """ Runs losing procedure (triggered when mine is hit). """
        space()
        self.display_game(border=True)
        lose_message()
        if self.end_game_procedure() == 'q':
            return 'q'

    def win_procedure(self):
        """ Runs winning procedure (triggered when mine is hit). """
        space()
        self.display_game(border=True)
        win_message()
        if self.end_game_procedure() == 'q':
            return 'q'

    def end_game_procedure(self):
        """ Runs end game procedure (regardless of win or loss). """
        print(f'  {REPLAY_MENU}\n')
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
    options_input = input('format: rows  columns  probability(optional, max 0.85)\n').split()
    # use default probability if it wasn't given
    probability = DEFAULT_MINE_CHANCE if len(options_input) < 3 else float(options_input[2])

    # ensures mine probability isn't too high and causes errors with empty drop
    while probability > 0.85:
        print('\nmine probability too high, may cause errors\n')
        options_input = input('format: rows  columns  probability(optional, max 0.85)\n').split()
        probability = DEFAULT_MINE_CHANCE if len(options_input) < 3 else float(options_input[2])

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

  {REPLAY_MENU}
            """)


def lose_message():
    print("""


               ===============
               == GAME OVER ==
               ===============

  {REPLAY_MENU}
            """)


def init_game():
    welcome_message()
    # prints a spacer to push get options message under welcome message
    print('           ', end='')
    rows, cols, prob = get_options()
    return User(rows, cols, prob)
