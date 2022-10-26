from collections.abc import Generator
from pprint import PrettyPrinter
from collections import deque
from game import Minesweeper
from time import sleep, time
from random import randint
from colors import *
import sys

""" This is the new improved CLI solver. It is the cleaned version of our OG solver,
before we move on to using GUI. It's been a great journey CLI, but it's time :,) """

""" I supposedly "cleaned and refactored" this file, but there's still tons of
extra commented out code and shit, and it's still pretty unclear what I can touch
without breaking the program, so this will be an ACTUAL refactor. (this is cli_solverV2 originally)
I'm gonna be removing all the notes about the new V2 algorithm, so if I need
to get that shit again I have to go to cli_solverV2. """

# == VISUALIZATION CONSTANTS ==
MOVE_DELAY = 0.02#2  # how long to delay before the bot makes a move
GRAPH_SEARCH_DELAY = 0.007  # how long to delay during a graph search step
SPACER = 50  # amount of lines to print to space boards out

# == GAME CONSTANTS ==
END_CHOICES = ('r', 'e', 'q')  # the available bot menu options
REPLAY_MENU = '(R) run bot again (Q) quit (E) edit settings'
DEFAULT_MINE_CHANCE = .15 # default mine probability
ADJACENT_COORDS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

pp = PrettyPrinter().pprint  # for dev stuff


class Solver(Minesweeper):
    """ Solver bot only has access to what a regular player could see, so it's completely fair. """

    def __init__(self, rows: int, cols: int, mine_spawn: float, chars_config: dict = None):
        super().__init__(rows, cols, mine_spawn, chars_config)
        self.solver_mask = self.gen_boolean_matrix()  # visual overlay that keeps track of the solver's progress
        self.solved = self.gen_boolean_matrix()  # stores a boolean matrix of the solved tiles
        self.solved_count = 0  # keeps count of number of solved tiles
        self.flag_tracker = 0  # keeps count of number of flags
        self.last_action = None  # holds last action played
        self.last_move = (None, None)  # keeps track of last coord played

    def solve(self):
        """ Starts solver/game by running start and update function. """
        self.starting = time()
        self.start()
        self.update()

    def start(self):
        """ Runs startup code for game (first iteration/move of the game). """
        space()
        self.display_mask()  # displays initial mask state

        # first move
        row, col = self.random_coords()  # picks random spot for first move
        self.find_empty_drop(row, col)  # regen board until there's a zero first move
        self.reveal(row, col)  # reveals spot once the 0 is found
        space()

        self.last_action = 'r'
        self.last_move = (row, col)

    def update(self):
        """ Runs solving loop. """
        while True:
            self.round_print()
            print()

            before = time()  # times how long the round takes =====

            # finds nearest number/chain and start grinding the chain
            chain = self.find_nearest_chain(*self.last_move)
            self.grind_chain(*chain)

            # if there's nothing more to be explored, it's a win
            if self.flag_tracker == self.mine_count:
                self.win_procedure()
                input('poop')

            after = time()  # ends round timer =====

            # TODO: run solving algorithm choose next row and col here
            row, col = self.persistent_drop()  # temporary random choice

            self.last_move = (row, col)  # NOTE: remember to always save last move
            action = self.last_action = 'r'  # TODO: decide if to reveal or flag

            sleep(self.decide_delay(after-before))  # delay before next move

            # executes choices: r | f | m
            if action == 'r':
                # checks if choice was a mine (and mask is unexplored) and ends game
                if self.isloss(row, col):
                    self.solver_mask[row][col] = self.color_string(self.chars['mine'], RED)
                    if self.losing_procedure() == 'q':
                        return 'q'
                    self.start()
                    if self.last_action == 'q':
                        return 'q'
                else:  # if no loss, continues revealing tile regularly
                    self.check_reveal(row, col)
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

    # ===== MAIN SOLVING ALGORITHMS =====
    def find_nearest_chain(self, r, c) -> tuple[int, int]:
        """ Depth first search from given coord and returns coord of first number/chain encountered. """
        stack = deque([(r, c)])  # use append to push, pop to pop
        discovered = set((r, c))  # hashset containing nodes already processed
        self.color_exposed(r, c, GREEN)  # marks the source node green

        while len(stack) > 0:  # while stack not empty
            curr = stack.pop()
            self.color_exposed(*curr, PURPLE)  # sets current node to purple

            # process node
            # NOTE: we don't check if it's integer cause the first thing we'll see after 0 HAS to be an integer
            if self.game[curr[0]][curr[1]] != 0:  # if we hit a number (chain), return its coords
                self.color_exposed(*curr, RED)  # sets destination node to red
                return curr
            self.color_exposed(*curr, CYAN)  # sets node to cyan once it's finished processing

            # add adjacent nodes
            for adj in self.adjacent_nodes(curr):
                """ NOTE: that means we bumped into an already completed chain,
                which is something we're gonna have to deal with in V2,
                maybe it gets fixed with lake scan. """
                if self.is_solved(*adj):  # NOTE: temp to catch the error but doesn't fix it!!
                    print('chain already solved, avoiding')
                    continue

                if adj not in discovered:
                    discovered.add(adj)
                    stack.append(adj)

    def grind_chain(self, r: int, c: int):
        """ Keeps running follow chain on number until the chain is completely solved. """
        last_progress = -1
        total_progress = self.flag_tracker + self.solved_count

        # stagnation detector
        while total_progress > last_progress:
            last_progress = total_progress  # current total progress becomes last progress
            self.follow_chain(r, c)
            total_progress = self.flag_tracker + self.solved_count  # current total progress is calculated

    def follow_chain(self, r: int, c: int):
        """ Follow chain of numbers (using bfs) starting at given coord and simple solve each node. """
        queue = deque([(r, c)])  # use append to enqueue, popleft to dequeue
        discovered = {(r, c)}  # hashset containing nodes already discovered

        # while queue not empty (there's still nodes to traverse)
        while len(queue) > 0:
            curr = queue.popleft()  # pop next node to process
            self.color_exposed(*curr, PURPLE)  # colors current node purple when it's first popped from the queue

            # if tile hasn't already been solved, try solving it
            if not self.is_solved(*curr):
                # colors node green if simple solve says it was able to fully solve, else colors yellow
                self.color_exposed(*curr, GREEN if self.simple_solve(*curr) else YELLOW)
            # else tile was already solved so colors it back to green (cause it was turned purple when popped from queue)
            else:
                # this happens because the tile was solved during a previous run of follow chain
                self.color_exposed(*curr, GREEN)

            for adj in self.adjacent_nodes(curr):
                # this is different than regular BFS because we're only gonna BFS over certain nodes (ints over 0)
                if adj not in discovered and self.is_chain(*adj) and not self.is_new(*adj):
                    discovered.add(adj)
                    queue.append(adj)

    def simple_solve(self, r: int, c: int) -> bool:
        """ Runs the simple solving algorithm and returns whether tile was solved. """
        unrevealed_count, flag_count = self.count_tiles(r, c)
        mines_left = self.game[r][c] - flag_count  # the actual number of mines left to find

        # if mines left and unrevealed count match, then we know all unrevealed tiles are mines
        if mines_left == unrevealed_count:  # OLD NOTE: mines_left/unrevealed_count is equal to probability that mine is in that cell, which is something I may need to use later
            # if they're both 0, then it was already solved and just need to be marked as solved
            if mines_left == 0:
                self.solved[r][c] = True
                self.solved_count += 1
                return True

            # flags all unrevealed tiles
            for sr, sc in self.adjacent_nodes((r, c)):
                if self.is_new(sr, sc):
                    self.flag(sr, sc)
                    self.flag_tracker += 1
                    self.color_change(sr, sc, RED)  # marks flag red

        # no more mines left but still some unrevealed tiles, then reveals all unrevealed
        elif mines_left == 0:
            for sr, sc in self.adjacent_nodes((r, c)):
                if self.is_new(sr, sc):
                    self.reveal(sr, sc)
        # not enough information to solve tile
        else:
            return False

        # returns True here for all the cases that were able to solve
        self.solved[r][c] = True
        self.solved_count += 1
        return True

    def count_tiles(self, r: int, c: int) -> tuple[int, int]:
        # TODO: try to find better name for this function
        """ Returns number of unrevealed tiles and flags. """
        unrevealed_count = 0
        flagged_count = 0

        for sr, sc in self.adjacent_nodes((r, c)):
            # increments unrevealed counter
            if self.is_new(sr, sc):
                unrevealed_count += 1
            # increments flagged counter
            elif self.is_flag(sr, sc):
                flagged_count += 1

        return unrevealed_count, flagged_count

    # ===== SOLVING ALGORITHMS HELPER FUNCTIONS =====
    def is_solved(self, r: int, c: int) -> bool:
        """ Returns whether given coordinate is marked as solved. """
        return self.solved[r][c]

    def determine_if_solved(self, r: int, c: int):
        """ Determines and returns whether tile is completely solved.
            This is determined by checking if no adjacent tiles are unrevealed. """
        # as soon as an unrevealed tile is found, returns False and exits the function, no need to keep checking
        for sr, sc in self.adjacent_nodes((r, c)):
            if self.is_new(sr, sc):
                return False

        return True

    def is_chain(self, r: int, c: int) -> bool:
        """ Returns whether given tile is an integer that's not 0 (chain tile). """
        return type(self.game[r][c]) is int and self.game[r][c] != 0

    def is_flag(self, r: int, c: int) -> bool:
        """ Returns whether given tile was flagged by the bot. """
        # return self.solver_mask[r][c] == RED + self.chars['flag'] + END_COLOR
        return self.mask[r][c] == self.chars['flag']  # checks for flag in the game mask

    # ===== COLORING/SOLVER MASK FUNCTIONS =====
    def wipe_color(self, r: int, c: int):
        """ Sets node's color back to white (FROM GAME VALUE) and refreshes board. """
        self.solver_mask[r][c] = self.game[r][c]  # wipes color
        self.print_board()  # for visualization purposes

    def drop_effect(self, r: int, c: int):
        """ Removes the extra effect but not the color (ex. removes bold). """
        self.solver_mask[r][c] = self.solver_mask[r][c][4:]

    def drop_color(self, r: int, c: int):
        """ Removes the top color (ex. used for switching colors). """
        self.solver_mask[r][c] = self.solver_mask[r][c][4:]

    def switch_color(self, r: int, c: int, new_color: str):
        """ Drops the top color and adds new color instead. """
        self.drop_color(r, c)
        self.solver_mask[r][c] = new_color + self.solver_mask[r][c]

    def color_string(self, white_string: str, color: str) -> str:
        """ Converts string to given color. """
        return color + white_string + END_COLOR

    def check_mask_color(self, r: int, c: int, color: str) -> bool:
        """ Checks if given coord's mask color matches the given color. """
        return self.solver_mask[r][c][:5] == color

    def color_cell(self, r: int, c: int, color: str):
        """ Changes the color of a given coord on the board. """
        self.solver_mask[r][c] = self.color_string(str(self.mask[r][c]), color)

    def expose(self, r: int, c: int):
        """ Sets mask of this node its game board value. """
        self.solver_mask[r][c] = self.game[r][c]

    def color_change(self, r: int, c: int, color: str):
        """ Wrapper for color cell to also print board and delay graph search. """
        self.color_cell(r, c, color)  # for visualization purposes
        self.print_board()  # for visualization purposes
        sleep(GRAPH_SEARCH_DELAY)

    def color_exposed(self, r: int, c: int, color: str):
        """ First exposes node (game board to mask) and changes color. """
        self.expose(r, c)
        self.color_change(r, c, color)

    def underline_node(self, r: int, c: int):
        """ Adds underline on top of given node's existing styling, then refreshes board. """
        self.solver_mask[r][c] = UNDERLINE + str(self.solver_mask[r][c])  # underline the node
        self.print_board()  # refreshes board

    def bold_node(self, r: int, c: int):
        """ Adds bold on top of given node's existing styling, then refreshes board. """
        self.solver_mask[r][c] = BOLD + str(self.solver_mask[r][c])  # bolds the node
        self.print_board()  # refreshes board

    # DISPLAY MASK (overwrites display mask from Minesweeper parent class)
    def display_mask(self):
        """ Overwrites display mask to implement use of separate solver mask. """
        # == X-AXIS ==
        constructed = '   '

        # prints the numbers first
        for num in self.cguide:
            constructed += str(num) + ' '
        constructed += '\n'

        # then prints the little ticks
        constructed += '   '
        for i in range(self.cols):
            constructed += '| '
        constructed += '\n'

        # == Y-AXIS & BOARD ==
        for r in range(self.rows):

            constructed += f'{self.rguide[r]}--'  # prints the guide: number + tick

            """ Solver mask is always a subset of mask, it can contain up to as much info as the main mask, but never more
            Solver Mask: #####1323##212#########1212###########
                   Mask: ###1213232321223#####23121234#########
            """

            # goes through every tile in the row and gets mask symbol
            for c in range(self.cols):
                # first checks if solver mask has traversed this area
                if self.solver_mask[r][c] is not False:
                    constructed += self.solver_mask[r][c]
                    constructed += ' '  # adds space between every character added
                    continue

                # and continues to regular mask if solver mask was empty there
                tile = self.mask[r][c]
                if tile is False:  # unexplored tile
                    constructed += self.chars['tile']
                elif tile == 0:  # empty tile (zero)
                    constructed += self.chars['zero']
                elif isinstance(tile, int):  # number tile
                    # NOTE: REMEMBER, boolean also gets called an int in isinstance
                    constructed += str(tile)
                elif isinstance(tile, str):  # should only happen if altered by solver for color
                    constructed += tile

                # this shouldn't activate for a solver display because it would've been caught in the solver mask layer
                else:  # other chars: flag, maybe, etc.
                    constructed += tile
                    input('poopoo')
                constructed += ' '  # adds space between every character added

            constructed += '\n'  # adds new line at end of the row

        # NOTE: trying stdout incase it prints faster and stutters less
        # print(constructed)
        sys.stdout.write(constructed)

    def round_print(self):
        """ Prints the last move, mask, and input guide for the round. """
        print(f'last move: {self.str_lmove()}\n')
        self.display_mask()  # displays game to user
        print('\n')

    def check_reveal(self, r: int, c: int):
        """ Checks if the coord chosen in a win or loss before revealing. """
        # checks if choice was a mine (and mask is unexplored) and ends game
        if self.isloss(r, c):
            self.solver_mask[r][c] = self.color_string(self.chars['mine'], RED)
            if self.losing_procedure() == 'q':
                exit()# return 'q'
            self.start()
            if self.last_action == 'q':
                exit()# return 'q'
        else:  # if no loss, continues revealing tile regularly
            self.reveal(r, c)
            if self.iswin():  # if there's nothing more to be explored, it's a win
                if self.win_procedure() == 'q':
                    exit()# return 'q'
                self.start()
            if self.last_action == 'q':
                exit()# return 'q'

    def losing_procedure(self):
        """ Runs losing procedure (triggered when mine is hit). """
        space()
        duration = time() - self.starting
        self.display_color_game()
        print(f'algorithm took {duration} seconds to run, nice 😈 genius')
        lose_message()
        if self.end_game_procedure() == 'q':
            return 'q'

    def win_procedure(self):
        """ Runs winning procedure (triggered when mine is hit). """
        space()
        duration = time() - self.starting
        self.display_color_game()
        print(f'algorithm took {duration} seconds to run, nice 😈 genius')
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
                elif isinstance(self.solver_mask[r][c], str):  # should only happen if altered by solver for color
                    print(self.solver_mask[r][c], end=' ')
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

    def persistent_drop(self) -> tuple[int, int]:
        """ Keeps dropping until it hits a zero. """
        while True:  # keep going while you're not getting zero
            row, col = self.unvisited_random()
            if self.mask[row][col] != 0:
                self.reveal(row, col)
            else:
                return (row, col)

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
    options_input = input('format: rows  columns  probability(optional, max 0.28)\n').split()
    # use default probability if it wasn't given
    probability = DEFAULT_MINE_CHANCE if len(options_input) < 3 else float(options_input[2])
    # ensures mine probability isn't too high and causes errors with empty drop
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
    print_bot_title()  # for dev testing
    print('           ', end='')  # prints a spacer to push get options message under welcome message
    rows, cols, prob = get_options()
    return Solver(rows, cols, prob)
