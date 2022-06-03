from game import Minesweeper
from random import randint
from time import sleep, time


MOVE_DELAY = .5  # how much to delay before the bot makes a move
SPACER = 50  # amount of lines to print to space boards out
END_CHOICES = ['r', 'e', 'q']  # the available bot menu options
REPLAY_MENU = '(R) run bot again (Q) quit (E) edit settings'
DEFAULT_MINE_CHANCE = .2 # default mine probability
# CHOICES = ['r', 'f', 'm', 'q']  # the available menu options  // no choices because you can't select anything as it's running
# FIXME: might need to do file for solver display, and then file for solver algorithms.
#        cause unlike user, solver is display + other backend.

# NOTE: remember to only give the bot access to what a regular player could see to make it accurate.
class Solver(Minesweeper):

    def __init__(self, rows: int, cols: int, mine_spawn: float, chars_config: dict = None):
        super().__init__(rows, cols, mine_spawn, chars_config)
        self.last_action = None
        self.last_move: tuple[int, int] = (None, None)

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

        self.last_action = 'r'
        self.last_move = (row, col)

    def update(self):
        """ Runs solving loop. """
        while True:
            # catches all errors and logs them to error.txt so game doesn't crash
            try:
                self.round_print()
                """ NOTE: Maybe once I write the solving algorithm,
                I should have it do solving algorithm and then whatever time is left
                after figuring out the next move, I will delay only that. """
                print()

                before = time()  # before main bot algorithm ====

                # TODO: run solving algorithm choose row and col here
                row, col = self.random_coords()  # temporary random choice

                after = time()  # after main bot algorithm ======

                self.last_move = (row, col)  # NOTE: remember to always save last move
                action = self.last_action = "TODO: decide if to reveal or flag"

                sleep(self.decide_delay(after-before))  # delay before next move

                # executes choices: r | f | m
                if action == 'r':
                    # checks if choice was a mine (and mask is unexplored) and ends game
                    if self.isloss(row, col):
                        if self.losing_procedure() == 'q':
                            return 'q'
                        self.start()
                        if self.last_action == 'q':
                            return 'q'
                    else:  # if no loss, continues revealing tile regularly
                        self.reveal(row, col)
                        if self.iswin():  # if there's nothing more to be explored, it's a win
                            if self.win_procedure() == 'q':
                                return 'q'
                            self.start()
                        if self.last_action == 'q':
                            return 'q'
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

    def round_print(self):
        """ Prints the last move, mask, and input guide for the round. """
        print(f'last move: {self.str_lmove()}\n')
        self.display_mask()  # displays game to user
        print('\n')

    def losing_procedure(self):
        """ Runs losing procedure (triggered when mine is hit). """
        space()
        self.display_game()
        lose_message()
        if self.end_game_procedure() == 'q':
            return 'q'

    def win_procedure(self):
        """ Runs winning procedure (triggered when mine is hit). """
        space()
        self.display_game()
        win_message()
        if self.end_game_procedure() == 'q':
            return 'q'

    def end_game_procedure(self):
        """ Runs end game procedure (regardless of win or loss). """
        print(f'  {REPLAY_MENU}\n')
        end_choice = input().lower()
        # keeps looping until proper end game choice
        while end_choice not in END_CHOICES:
            print('\n choice doesn\'t exist, only: R | E | Q')
            end_choice = input().lower()
        if end_choice == 'r':  # run bot again
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

    def decide_delay(self, time_elapsed) -> float:
        """ Returns how much longer to delay move after calculating next move. """
        if time_elapsed >= MOVE_DELAY:
            return 0
        else:
            return MOVE_DELAY - time_elapsed

    def str_lmove(self) -> str:
        """ Returns last move but stringified. """
        return f'{self.last_action} {self.last_move[0]} {self.last_move[1]}'


def get_options() -> tuple[int, int, float]:
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
            """)
    sleep(1.5)
    print("""

               @({{$*#%}":@$&)#^&#%&@@{^&!^&)$#E^&@
               !@{^&!%                      \@$&)#!
               $&@$&)  The Bot Version 🤖💣  {^&!)$
               &$#E^&:                      $*#%}"U
               *#@#(^%&@@{^}{|$G@@$#$@^&":@{^&!^&)$
            """)
    sleep(2)
    print("""

                    To get started, input your
             desired dimensions and mine probability.
            """)
    sleep(2)
    print("""
            #$%*}#G  and I'll do the rest 😈  ^&$@#$%



            """)

def dev_welcome_message():
    """ Tweaked welcome message w/o delays for when I'm repeatedly running. """
    print("""

               @({{$*#%}":@$&)#^&#%&@@{^&!^&)$#E^&@
               !@{^&!%                      \@$&)#!
               $&@$&)  The Bot Version 🤖💣  {^&!)$
               &$#E^&:                      $*#%}"U
               *#@#(^%&@@{^}{|$G@@$#$@^&":@{^&!^&)$
            """)

def win_message():
    print(f"""


               ===============
               == YOU WIN!! ==
               ===============

  {REPLAY_MENU}
            """)

def lose_message():
    print(f"""


               ===============
               == GAME OVER ==
               ===============

  {REPLAY_MENU}
            """)

def init_solver():
    dev_welcome_message()
    print('           ', end='')  # prints a spacer to push get options message under welcome message
    rows, cols, prob = get_options()
    return Solver(rows, cols, prob)