from game import Minesweeper
from random import randint
from time import sleep, time


MOVE_DELAY = .5  # how much to delay before the bot makes a move
SPACER = 50  # amount of lines to print to space boards out
# CHOICES = ['r', 'f', 'm', 'q']  # the available menu options
# END_CHOICES = ['p', 'e', 'q']  # the available end game options
# FIXME: might need to do file for solver display, and then file for solver algorithms.
#        cause unlike user, solver is display + other backend.

# NOTE: remember to only give the bot access to what a regular player could see to make it accurate.
class Solver(Minesweeper):

    def __init__(self, rows: int, cols: int, mine_spawn: float, chars_config: dict = None):
        super().__init__(rows, cols, mine_spawn, chars_config)

    def solve(self):
        """ Starts solver/game by running start and update function. """
        self.start()
        self.update()

    def start(self):
        """ Runs startup code for game (first loop of game). """
        space()

        self.display_mask()  # displays initial mask state

        row, col = self.random_coords()
        self.find_empty_drop(row, col)  # regen board until there's a zero under choice
        self.reveal(row, col)  # reveals spot once the 0 is found
        space()

        return f'r {row}, {col}'  # returns last move

    def update(self):
        """ Runs solving loop. """
        while True:
            # catches all errors and logs them to error.txt so game doesn't crash
            try:
                self.round_print(last_move)
                """ NOTE: Maybe once I write the solving algorithm,
                I should have it do solving algorithm and then whatever time is left
                after figuring out the next move, I will delay only that. """

                print()

                before = time()
                # TODO: run solving algorithm choose row and col here
                row, col = self.random_coords()
                action = "TODO: decide if to reveal or flag"
                      # TEMPORARY ^^
                after = time()
                sleep(self.decide_delay(after-before))  # delay before next move

                # executes choices: r | f | m
                if action == 'r':
                    # checks if choice was a mine (and mask is unexplored) and ends game
                    if self.isloss(row, col):
                        self.losing_procedure()
                    else:  # if no loss, continues revealing tile regularly
                        self.reveal(row, col)
                        if self.iswin():  # if there's nothing more to be explored, it's a win
                            self.win_procedure()
                            last_move = self.start()
                elif action == 'f':
                    self.flag(row, col)
                elif action == 'm':
                    self.maybe(row, col)
                space()

            except Exception as e:
                with open('solver_error_log.txt', 'a+') as error_file:
                    error_file.write('LINE NUMBER: ' + str(e.__traceback__.tb_lineno))
                    error_file.write(f'\n{str(e)}\n')
                print('~~ error logged to file ~~')

    def round_print(self, last_move: str):
        """ Prints the last move, mask, and input guide for the round. """
        print(f'last move: {last_move}\n')
        self.display_mask()  # displays game to user
        print('\n')

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

    def random_coords(self) -> tuple[int, int]:
        """ Randomly generates coords. """
        return randint(0, self.rows-1), randint(0, self.cols-1)

    def random_drop(self, row: int, col: int):
        """ Randomly picks coord to drop onto. """
        self.reveal(row, col)

    def persistent_drop(self):
        """ Keeps dropping until it hits a zero. """
        row, col = self.random_coords()
        self.reveal(row, col)
        while self.mask[row][col] != 0:  # keep going while you're not getting zero
            row, col = self.random_coords()
            self.reveal(row, col)

    def decide_delay(self, time_elapsed):
        """ Returns how much longer to delay move after calculating next move. """
        if time_elapsed >= MOVE_DELAY:
            return 0
        else:
            return MOVE_DELAY - time_elapsed

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