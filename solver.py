from collections.abc import Generator
from pprint import PrettyPrinter
from collections import deque
from game import Minesweeper
from time import sleep, time
from random import randint
from colors import *


pp = PrettyPrinter().pprint
MOVE_DELAY = .8  # how long to delay before the bot makes a move
GRAPH_SEARCH_DELAY = .05  # how long to delay during a graph search step
SPACER = 50  # amount of lines to print to space boards out
END_CHOICES = ['r', 'e', 'q']  # the available bot menu options
REPLAY_MENU = '(R) run bot again (Q) quit (E) edit settings'
DEFAULT_MINE_CHANCE = .15 # default mine probability
ADJACENT_COORDS = [(r, c) for r in range(-1, 2) for c in range(-1, 2)]
ADJACENT_COORDS.pop(4)
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
        print(row, col)
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
                self.dfs(*self.last_move)
                after = time()  # after main bot algorithm ======
                # print(after-before)

                # TODO: run solving algorithm choose row and col here
                row, col = self.unvisited_random()  # temporary random choice

                self.last_move = (row, col)  # NOTE: remember to always save last move
                action = self.last_action = 'r'  # TODO: decide if to reveal or flag

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

    def bfs(self, r, c) -> tuple[int, int]:
        """ Breadth first search around coord and returns coord of first wall encountered. """
        queue = deque([(r, c)])  # use append to enqueue, popleft to dequeue
        checked = set((r, c))  # hashset containing nodes already processed
        self.color_change((r, c), GREEN)  # marks the source node green

        while len(queue) > 0:  # while queue not empty
            curr = queue.popleft()
            self.color_change(curr, PURPLE)  # sets current node to purple

            if curr not in checked:  # if this node hasn't been checked yet
                # if we hit a number, return its coords
                if self.game[curr[0]][curr[1]] != 0:
                    self.color_change(curr, RED)  # sets destination node to red
                    return curr
                checked.add(curr)

            # check next breadth of nodes
            for adj in self.adjacent_nodes(curr):
                # the bounds makes sure it doesn't try searching outside the board
                if adj not in checked and adj not in queue and self.bounds(*adj):
                    queue.append(adj)

            self.color_change(curr, CYAN)  # sets processed node to cyan

        self.color_change((r, c), GREEN)  # remarks the source node to green because it gets overwritten

    def dfs(self, r, c) -> tuple[int, int]:
        """ Depth first search around coord and returns coord of first wall encountered. """
        stack = deque([(r, c)])  # use append to push, pop to pop
        checked = set((r, c))  # hashset containing nodes already processed
        self.color_change((r, c), GREEN)  # marks the source node green

        while len(stack) > 0:  # while stack not empty
            curr = stack.pop()
            self.color_change(curr, PURPLE)  # sets current node to purple

            if curr not in checked:  # if this node hasn't been checked yet
                # if we hit a number, return its coords
                if self.game[curr[0]][curr[1]] != 0:
                    self.color_change(curr, RED)  # sets destination node to red
                    return curr
                checked.add(curr)

            # checks neighbors
            for adj in self.adjacent_nodes(curr):
                # the bounds makes sure it doesn't try searching outside the board
                if adj not in checked and adj not in stack and self.bounds(*adj):
                    stack.append(adj)

            self.color_change(curr, CYAN)  # sets processed node to cyan

        self.color_change((r, c), GREEN)  # remarks the source node to green because it gets overwritten

    def adjacent_nodes(self, curr: tuple[int, int]) -> Generator[tuple[int, int]]:
        """ Returns the coords of the surrounding nodes. """
        for offset_c in ADJACENT_COORDS:
            yield self.offset_coord(curr, offset_c)

    def offset_coord(self, coord: tuple[int, int], offset: tuple[int, int]) -> tuple[int, int]:
        """ Returns a coord with the given offset. """
        return tuple(x + y for x, y in zip(coord, offset))

    def color_string(self, white_string: str, color: str) -> str:
        """ Converts string to given color. """
        return color + white_string + END_COLOR

    def color_cell(self, coord: tuple[int, int], color: str):
        """ Changes the color of a given coord on the board. """
        self.mask[coord[0]][coord[1]] = self.color_string(str(self.game[coord[0]][coord[1]]), color)

    def color_change(self, coord: tuple[int, int], color: str):
        """ Wrapper for color change to also print board and delay graph search. """
        self.color_cell(coord, color)  # for visualization purposes
        self.print_board()  # for visualization purposes
        sleep(GRAPH_SEARCH_DELAY)

    def round_print(self):
        """ Prints the last move, mask, and input guide for the round. """
        print(f'last move: {self.str_lmove()}\n')
        self.display_mask()  # displays game to user
        print('\n')

    def losing_procedure(self):
        """ Runs losing procedure (triggered when mine is hit). """
        space()
        self.display_color_game()
        lose_message()
        if self.end_game_procedure() == 'q':
            return 'q'

    def win_procedure(self):
        """ Runs winning procedure (triggered when mine is hit). """
        space()
        self.display_color_game()
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
#30 50
    def display_color_game(self, border: bool = True):
        """ Variation of the display_game() function where it prints the color too. """
        if border:
            print('-'*(self.cols*2+3))
        for r in range(self.rows):
            if border:
                print('|', end=' ')
            for c in range(self.cols):
                tile = self.game[r][c]
                if tile is True:  # mine
                    print(self.chars['mine'], end=' ')
                elif isinstance(self.mask[r][c], str):  # should only happen if altered by solver for color
                    print(self.mask[r][c], end=' ')
                elif tile == 0:  # empty tile (zero)
                    print(self.chars['zero'], end=' ')
                elif type(tile) is int:  # number tile
                    print(str(tile), end=' ')
            if border:
                print('|', end='')
            print()
        if border:
            print('-'*(self.cols*2+3))

    def random_coords(self) -> tuple[int, int]:
        """ Randomly generates coords. """
        return randint(0, self.rows-1), randint(0, self.cols-1)

    def unvisited_random(self) -> tuple[int, int]:
        """ Randomly generates coords that haven't been visited yet. """
        random_coord_pick = self.random_coords()
        while not self.is_new(*random_coord_pick):
            random_coord_pick = self.random_coords()
        return random_coord_pick

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

    def test_board(self):
        """ Regenerates game board to same very empty board (allows repeated testing on constant board). """
        self.mines = [[False]*self.cols]*self.rows  # base list, all False
        # handles left and right sides
        for r in range(self.rows):
            self.mines[r][0] = True
            self.mines[r][self.cols-1] = True
        # handles top and bottom sides
        self.mines[0] = [True]*self.cols
        self.mines[self.cols-1] = [True]*self.cols
        self.mine_count = self.area - ((self.rows-2)*(self.cols-2))

        self.game = [[True, 5, 3, *[0]*(self.cols-6), 3, 5, True] for rowwwewaew in range(self.rows)]
        self.game[1] = [True, *[5]*(self.cols-2), True]
        self.game[self.cols-2] = [True, *[5]*(self.cols-2), True]
        self.game[2] = [True, 5, *[3]*(self.cols-4), 5, True]
        self.game[self.cols-3] = [True, 5, *[3]*(self.cols-4), 5, True]
        self.game[0] = [True]*self.cols
        self.game[self.cols-1] = [True]*self.cols

        # rest is the regen_board() code but without the mine generation part because that's the part we're taking control of
        self.mask = self.gen_mask_board()  # the board as seen by the user
        # self.display_game()
        self.mask_tile_count = 0

def get_options() -> tuple[int, int, float]:
    """ Gets game options: rows, columns, and mine probability. """
    options_input = input('format: rows  columns  probability(optional, max 0.28)\n').split()
    # use default probability if it wasn't given
    probability = DEFAULT_MINE_CHANCE if len(options_input) < 3 else float(options_input[2])
    # ensures mine probability isn't too high and causes errors with empty drop
    # FIX: ERROR
    while probability > 0.28:
        print('\nmine probability too high, may cause errors\n')
        options_input = input('format: rows  columns  probability(optional, max 0.28)\n').split()
        probability = DEFAULT_MINE_CHANCE if len(options_input) < 3 else float(options_input[2])

    return int(options_input[0]), int(options_input[1]), probability

def calc_runtime(func, arguments: tuple or list) -> float:
    """ Times how long it takes for given function to run. """
    before = time()
    func(*arguments)
    after = time()
    return after - before

def space():
    print('\n'*SPACER)

def welcome_message():
    print("""


               ====================================
               === WELCOME TO MINESWEEPER! 💣🧹 ===
               ====================================
            """)
    sleep(1.5)
    print_bot_title()
    sleep(2)
    print("""

                    To get started, input your
             desired dimensions and mine probability.
            """)
    sleep(2)
    print(f"""
            {RED}#$%*}}#G{END_COLOR}  and I'll do the rest 😈  {RED}^&$@#$%{END_COLOR}



            """)

def dev_welcome_message():
    """ Tweaked welcome message w/o delays for when I'm repeatedly running. """
    print_bot_title()

def print_bot_title():
    """ Tweaked welcome message w/o delays for when I'm repeatedly running. """
    print(f"""{RED}

               @({{{{$*#%}}":@$&)#^&#%&@@{{^&!^&)$#E^&@
               !@{{^&!%                      \@$&)#!
               $&@$&){END_COLOR}  The Bot Version 🤖💣  {RED}{{^&!)$
               &$#E^&:                      $*#%}}"U
               *#@#(^%&@@{{^}}{{|$G@@$#$@^&":@{{^&!^&)${END_COLOR}
            """)

def win_message():
    print(f"""


               ===============
               == YOU WIN!! ==
               ===============

""")

def lose_message():
    print(f"""


               ===============
               == GAME OVER ==
               ===============

""")

def init_solver():
    # welcome_message()
    print_bot_title()  # for dev testing
    print('           ', end='')  # prints a spacer to push get options message under welcome message
    rows, cols, prob = get_options()
    return Solver(rows, cols, prob)
