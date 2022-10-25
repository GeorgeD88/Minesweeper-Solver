from collections.abc import Generator
from pprint import PrettyPrinter
from collections import deque
from game import Minesweeper
from time import sleep, time
from random import randint
from colors import *
import sys

""" CLI solver is basically the refactor file of solver,
    but once it's completely clean and refactored I'm gonna make it into a GUI,
    so this will become solver, but CLI version. """

# == VISUALIZATION CONSTANTS ==
MOVE_DELAY = 0.2  # how long to delay before the bot makes a move
GRAPH_SEARCH_DELAY = 0.007  # how long to delay during a graph search step
SPACER = 50  # amount of lines to print to space boards out

# == GAME CONSTANTS ==
END_CHOICES = ('r', 'e', 'q')  # the available bot menu options
REPLAY_MENU = '(R) run bot again (Q) quit (E) edit settings'
DEFAULT_MINE_CHANCE = .15 # default mine probability
ADJACENT_COORDS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

pp = PrettyPrinter().pprint  # for dev stuff

""" FIXME: might need to do file for solver display, and then file for solver algorithms.
        cause unlike user, solver is a display overlay + other backend.
        This might be fine here but could be important for GUI version. """


class Solver(Minesweeper):
    """ Solver bot only has access to what a regular player could see, so it's completely fair. """

    def __init__(self, rows: int, cols: int, mine_spawn: float, chars_config: dict = None):
        super().__init__(rows, cols, mine_spawn, chars_config)
        self.solver_mask = self.gen_mask_board()  # visual overlay that keeps track of the solver's progress
        self.completed = self.gen_mask_board()  # stores a boolean matrix of the solved tiles
        self.solved_count = 0  # keeps count of number of solved tiles
        self.flag_tracker = 0  # keeps count of number of flags
        self.last_action = None  # holds last action played, NOTE: I don't think this is relevant for solver
        self.last_move = (None, None)  # keeps track of last coord played

    def solve(self):
        """ Starts solver/game by running start and update function. """
        self.start()
        self.update()

    def solveV2(self):
        """ MS-Solver Algorithm V2, the whole algorithm is a linear list of operations. """

        # [1] 🎲📍 Random drop to open up the board
        """ Simply drop in a random place to open up the board and begin the algorithm. """
        self.start()

        # [2] 🔎🏝️ Scan initial lake for islands (*island scan*)
        """ As the algorithm progresses, I will have to make an algorithm to detect
        when we open up a new lake, and whenever a lake is opened, run island scan on it
        and keep track of all the islands to make sure we traverse them later. """
        pass # initial drop will always open up a lake, so need to check for lake
        pass # self.island_scan()  # this will store islands (maybe in class variable)
        # make sure to store initial lake chain coords

        # [3] ⛏️⛓️ Phase 1 simple solving: Iterate through the marked chains (lake and island borders) and run *grind chain* on them
        """ I call this phase 1 because this is the first wave of traversing and solving the board,
        and you only use simple solving in this phase. Also run *island scan* every time you open up a new lake. """
        pass # for island in self.islands:
        pass #     self.grind_chain(island[0])

        # wall = self.dfs(*self.last_move)  # finds nearest number
        # self.grind_chain(*wall)
        # because we had island scan fill up the lake, we already have the coords for the lake chain and don't need to dfs for it
        pass # self.grind_chain(*initial_lake)

        # [4] 🕵️📈 Phase 2 pattern recognition/breaking stagnation: Traverse board looking for patterns to open up new info.
        """ Traverse the board looking for patterns. If a pattern is recognized, use the info you get from the pattern to reveal/flag more tiles,
        and then check if you're able to solve any of the surrounding tiles now (meaning stagnation was broken). If so, run grind chain from there
        and it will BFS out solving more tiles from the information discovered. """
        pass # find patterns*
        # within find_patterns, whenever a pattern is found:
        pass # after revealing/flagging using new info from pattern, check if *stagnation was broken*
             # by checking if you can simple solve the pattern tiles or surroundings
             # if you can then stagnation was broken so run a simple solve *grind chain* starting at the pattern.

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
            # catches all errors and logs them to error.txt so game doesn't crash
            # try:
            self.round_print()
            print()

            before = time()  # times how long the round takes =====

            # finds nearest number/chain and start grinding the chain
            chain = self.dfs(*self.last_move)
            self.grind_chain(*chain)

            # if there's nothing more to be explored, it's a win
            if self.flag_tracker == self.mine_count:
                self.win_procedure()
                input('poop')
            # wall = self.bfs_zero_fill(*self.last_move)  # finds nearest number
            # last_border_touched = set()
            # border_touched = self.mark_wall(*wall)
            # while len(border_touched) > len(last_border_touched):
            #     if not wall:  # didn't hit any number means board is empty:
            #         self.win_procedure()
            #         exit()
            #     self.grind_chain(*wall)
            #     last_border_touched = border_touched
            #     wall = self.new_dfs(*self.last_move, last_border_touched)  # finds nearest number
            #     border_touched = self.mark_wall(*wall)
            #     # wall, border_touched = self.bfs_zero_fill(*self.last_move)  # finds nearest number

            """ walls = set()
            while True:
                wall = self.bfs(*self.last_move)  # finds nearest number
                if wall in walls:  # break if all numbers connected to this one have been solved
                    break
                walls.add(wall)  # adds wall to visited walls
                self.grind_chain(*wall)
                print('chain: GRINDED')
                # exit() """

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
                    self.mask[row][col] = self.color_string(self.chars['mine'], RED)
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

            # except Exception as e:
            #     with open('slver_error_log.txt', 'a+') as error_file:
            #         error_file.write('LINE NUMBER: ' + str(e.__traceback__.tb_lineno))
            #         error_file.write(f'\n{str(e)}\n')
            #     print('~~ error logged to file ~~')

    # BREADTH FIRST SEARCH ALGORITHM
    def bfs(self, r, c) -> tuple[int, int]:
        """ Breadth first search around coord and returns coord of first wall encountered. """
        queue = deque([(r, c)])  # use append to enqueue, popleft to dequeue
        checked = set()  # hashset containing nodes already processed
        checked.add((r, c))  # we already know this node is gonna be a 0 so no need to check it
        self.color_exposed((r, c), GREEN)  # marks the source node green

        while len(queue) > 0:  # while queue not empty
            curr = queue.popleft()
            self.color_exposed(curr, PURPLE)  # sets current node to purple

            if curr not in checked:  # if this node hasn't been checked yet
                # if we hit a number, return its coords
                if self.game[curr[0]][curr[1]] != 0:
                    self.color_exposed(curr, RED)  # sets destination node to red
                    self.bold_node((r, c))  # bolds the source node
                    return curr
                checked.add(curr)

            self.color_exposed(curr, CYAN)  # sets processed node to cyan

            # check next breadth of nodes
            for adj in self.adjacent_nodes(curr):
                # the bounds makes sure it doesn't try searching outside the board
                if adj not in checked and adj not in queue and self.bounds(*adj):
                    queue.append(adj)

    def bfs_zero_fill(self, r, c) -> tuple[int, int]:
        """ Breadth first search around coord but fills whole pool with zeros before returning coord. """
        queue = deque([(r, c)])  # use append to enqueue, popleft to dequeue
        checked = set()  # hashset containing nodes already processed
        checked.add((r, c))  # we already know this node is gonna be a 0 so no need to check it
        self.color_exposed((r, c), GREEN)  # marks the source node green
        coord_found = None

        while len(queue) > 0:  # while queue not empty
            curr = queue.popleft()
            self.color_exposed(curr, PURPLE)  # sets current node to purple

            if curr not in checked:  # if this node hasn't been checked yet
                # if we hit a number, return its coords
                if not coord_found and self.game[curr[0]][curr[1]] != 0:
                    self.color_exposed(curr, RED)  # sets destination node to red
                    coord_found = curr
                checked.add(curr)

            if isinstance(self.game[curr[0]][curr[1]], int) and self.game[curr[0]][curr[1]] != 0:
                self.wipe_color(curr)
            else:
                self.color_exposed(curr, CYAN)  # sets processed node to cyan

            # check next breadth of nodes
            for adj in self.adjacent_nodes(curr):
                # the bounds makes sure it doesn't try searching outside the board
                if coord_found and isinstance(self.game[curr[0]][curr[1]], int) and self.game[curr[0]][curr[1]] != 0:
                    continue
                elif adj not in checked and adj not in queue and self.bounds(*adj):
                    queue.append(adj)

        self.color_exposed(coord_found, RED)  # sets destination node to red
        self.bold_node((r, c))  # bolds the source node
        return coord_found

    # DEPTH FIRST SEARCH ALGORITHM
    def dfs(self, r, c) -> tuple[int, int]:
        """ Depth first search around coord and returns coord of first wall encountered. """
        stack = deque([(r, c)])  # use append to push, pop to pop
        checked = set()  # hashset containing nodes already processed
        checked.add((r, c))  # we already know this node is gonna be a 0 so no need to check it
        self.color_exposed((r, c), GREEN)  # marks the source node green

        while len(stack) > 0:  # while stack not empty
            curr = stack.pop()
            self.color_exposed(curr, PURPLE)  # sets current node to purple

            if curr not in checked:  # if this node hasn't been checked yet
                # if we hit a number, return its coords
                if self.game[curr[0]][curr[1]] != 0:
                    self.color_exposed(curr, RED)  # sets destination node to red
                    return curr
                checked.add(curr)

            self.color_exposed(curr, CYAN)  # sets processed node to cyan

            # checks neighbors
            for adj in self.adjacent_nodes(curr):
                # that means this bumped into an already completed wall
                if not self.bounds(*adj):
                    continue
                if self.is_completed(*adj):
                    input('chick chick, BOOOMMM')
                    return adj
                if adj not in checked and adj not in stack:
                    stack.append(adj)

        # bolds source node and updates display
        self.bold_node((r, c))
        sleep(GRAPH_SEARCH_DELAY)

    def new_dfs(self, r, c, ) -> tuple[int, int]:
        """ Depth first search around coord and returns coord of first wall encountered. """
        stack = deque([(r, c)])  # use append to push, pop to pop
        checked = set()  # hashset containing nodes already processed
        checked.add((r, c))  # we already know this node is gonna be a 0 so no need to check it
        self.color_exposed((r, c), GREEN)  # marks the source node green

        while len(stack) > 0:  # while stack not empty
            curr = stack.pop()
            self.color_exposed(curr, PURPLE)  # sets current node to purple

            if curr not in checked:  # if this node hasn't been checked yet
                # if we hit a number, return its coords
                if self.game[curr[0]][curr[1]] != 0:
                    self.color_exposed(curr, RED)  # sets destination node to red
                    return curr
                checked.add(curr)

            self.color_exposed(curr, CYAN)  # sets processed node to cyan

            # checks neighbors
            for adj in self.adjacent_nodes(curr):
                # that means this bumped into an already completed wall
                if not self.bounds(*adj):
                    continue
                if self.is_completed(*adj):
                    input('chick chick, BOOOMMM')
                    return adj
                if adj not in checked and adj not in stack:
                    stack.append(adj)

        # bolds source node and updates display
        self.bold_node((r, c))
        sleep(GRAPH_SEARCH_DELAY)

    def dfs_zero_fill(self, r, c) -> tuple[int, int]:
        """ Breadth first search around coord but fills whole pool with zeros before returning coord. """
        stack = deque([(r, c)])  # use append to push, popleft to pop
        checked = set()  # hashset containing nodes already processed
        checked.add((r, c))  # we already know this node is gonna be a 0 so no need to check it
        self.color_exposed((r, c), GREEN)  # marks the source node green
        coord_found = None

        while len(stack) > 0:  # while stack not empty
            curr = stack.pop()
            self.color_exposed(curr, PURPLE)  # sets current node to purple

            if curr not in checked:  # if this node hasn't been checked yet
                # if we hit a number, return its coords
                if not coord_found and self.game[curr[0]][curr[1]] != 0:
                    self.color_exposed(curr, RED)  # sets destination node to red
                    coord_found = curr
                checked.add(curr)

            if isinstance(self.game[curr[0]][curr[1]], int) and self.game[curr[0]][curr[1]] != 0:
                self.wipe_color(curr)
            else:
                self.color_exposed(curr, CYAN)  # sets processed node to cyan

            # check next breadth of nodes
            for adj in self.adjacent_nodes(curr):
                # the bounds makes sure it doesn't try searching outside the board
                if coord_found and isinstance(self.game[curr[0]][curr[1]], int) and self.game[curr[0]][curr[1]] != 0:
                    continue
                elif adj not in checked and adj not in stack and self.bounds(*adj):
                    stack.append(adj)

        self.color_exposed(coord_found, RED)  # sets destination node to red
        self.bold_node((r, c))  # bolds the source node
        return coord_found

    def mark_wall(self, r: int, c: int):
        """ Runs BFS on given coord and marks the whole wall as checked. """
        queue = deque([(r, c)])
        marked = set()

        while len(queue) > 0:
            curr = queue.popleft()

            if not curr not in marked:
                marked.add(curr)

            for adj in self.adjacent_nodes(curr):
                if adj not in queue and adj not in marked:
                    queue.append(adj)

        return marked

    # ===== MAIN SOLVING ALGORITHMS =====
    def grind_chain(self, r: int, c: int):
        """ Keeps running follow chain on number until the chain is completely solved. """
        last_progress = -1
        total_progress = self.flag_tracker + self.solved_count
        # iter_counter = 1 DELETE

        # stagnation detector
        while total_progress > last_progress:
            last_progress = total_progress  # current total progress becomes last progress
            self.follow_chain(r, c)
            total_progress = self.flag_tracker + self.solved_count  # current total progress is calculated

            # DELETE --,
            # iter_counter += 1
        # input('finished grinding chain')
        # input(f'last progress: {last_progress}\nupdated progress: {total_progress}')

    def follow_chain(self, r: int, c: int):
        """ Follow chain of numbers (using bfs) starting at given coord and process each node. """
        queue = deque([(r, c)])  # use append to enqueue, popleft to dequeue
        processed = set()  # hashset containing nodes already processed

        while len(queue) > 0:  # while queue not empty
            curr = queue.popleft()
            self.color_exposed(curr, PURPLE)  # sets current node to yellow, so while it's being calculated it's yellow

            if curr not in processed:  # if this node hasn't been processed yet
                # input('solving')
                if not self.is_completed(*curr):
                    self.basic_solve(*curr)  # process node by running solving algorithm
                processed.add(curr)  # mark node as processed
            # else:
                # input(f'completion status: {self.is_completed(*curr)}')
                      #processed: {processed}\n
            # colors node green if it's completely solved and avoids coloring already green node
            if not self.is_completed(*curr):
                # input('not solved yet')
                self.color_exposed(curr, YELLOW)
            elif not self.check_mask_color(curr, GREEN):
                # input('completed but not green')
                self.color_exposed(curr, GREEN)
            else:
                actual_color = color_names[self.mask[curr[0]][curr[1]][:5]]
                input('huh?:' + actual_color if actual_color else ' blue pilled')

            # add next breadth of nodes to queue
            for adj in self.adjacent_nodes(curr):
                if adj in processed:
                    continue
                elif self.bounds(*adj) and self.game[adj[0]][adj[1]] != 0 and isinstance(self.game[adj[0]][adj[1]], int) and adj not in processed and adj not in queue and self.mines[adj[0]][adj[1]] is False:
                    queue.append(adj)

    # TODO
    # def solve_cell(self, r: int, c: int):
    #     """ Runs all solving algorithms in order from coarse to granular. """
    #     self.basic_solve(r, c)
    #     # run the rest once I code more

    def basic_solve(self, r: int, c: int):
        """ Runs the basic solving algorithm (clears majority of the board). """
        empty_count, flag_count = self.count_openNflags(r, c )
        mines_left = self.game[r][c] - flag_count  # mine count - flag count
        # input(f'empty: {empty_count}\nflag count: {flag_count}\nmines left: {mines_left}')
        # mines left and open count match, then we can clear this out
        if mines_left == empty_count:  # NOTE: mines_left/empty_count is equal to probability that mine is in that cell, which is something I may need to use later
            # input('clearing out')
            for sr, sc in self.adjacent_nodes((r, c)):
                if not self.bounds(sr, sc):
                    continue
                print(sr, sc)
                if self.is_new(sr, sc):
                    self.flag(sr, sc)
                    self.flag_tracker += 1
                    self.color_change((sr, sc), RED)  # marks flag red
            # input('checking completion')
            if self.record_completed(r, c):  # NOTE: this was extra
                self.completed[r][c] = True
                self.solved_count += 1
        elif mines_left == 0:  # and open count is not equal to it, then it has to be more
            for sr, sc in self.adjacent_nodes((r, c)):
                self.reveal(sr, sc)
        # else:
            # input('not enough info')
        # mines_left == empty_count, or mines_left < empty_count, but mines_left cannot be more than empty_count

    def count_openNflags(self, r: int, c: int) -> tuple[int, int]:
        """ Returns number of unexplored nodes and number of flags. """
        unexplored_nodes_count = 0
        flagged_nodes_count = 0
        for sr, sc in self.adjacent_nodes((r, c)):
            if not self.bounds(sr, sc):
                continue
            if self.is_new(sr, sc):
                unexplored_nodes_count += 1
            elif self.mask[sr][sc] == (RED + self.chars['flag'] + END_COLOR):
                flagged_nodes_count += 1
        return unexplored_nodes_count, flagged_nodes_count

    def is_completed(self, r: int, c: int) -> bool:
        """ Returns whether given coordinate is marked as completed in the hashmap. """
        return self.completed[r][c] is True

    def record_completed(self, r: int, c: int):
        """ Determines if node is done being calculated. """
        unexplored_nodes_count = 0
        for sr, sc in self.adjacent_nodes((r, c)):
            if self.bounds(sr, sc) and self.is_new(sr, sc):
                unexplored_nodes_count += 1
        return unexplored_nodes_count == 0

    # MASK COLORING  TODO: refactor to color on separate solver mask
    def wipe_color(self, coord: tuple[int, int]):
        """ Sets node's color back to white (FROM GAME VALUE) and refreshes board. """
        self.mask[coord[0]][coord[1]] = self.game[coord[0]][coord[1]]  # wipes color
        self.print_board()  # for visualization purposes

    def drop_effect(self, coord: tuple[int, int]):
        """ Removes the extra effect but not the color (ex. removes bold). """
        self.mask[coord[0]][coord[1]] = self.mask[coord[0]][coord[1]][4:]

    def drop_color(self, coord: tuple[int, int]):
        """ Removes the top color (ex. used for switching colors). """
        self.mask[coord[0]][coord[1]] = self.mask[coord[0]][coord[1]][4:]

    def switch_color(self, coord: tuple[int, int], new_color: str):
        """ Drops the top color and adds new color instead. """
        self.drop_color(coord)
        self.mask[coord[0]][coord[1]] = new_color + self.mask[coord[0]][coord[1]]

    def color_string(self, white_string: str, color: str) -> str:
        """ Converts string to given color. """
        return color + white_string + END_COLOR

    def check_mask_color(self, coord: tuple[int, int], color: str) -> bool:
        """ Checks if given coord's mask color matches the given color. """
        return self.mask[coord[0]][coord[1]][:5] == color

    def color_cell(self, coord: tuple[int, int], color: str):
        """ Changes the color of a given coord on the board. """
        self.mask[coord[0]][coord[1]] = self.color_string(str(self.mask[coord[0]][coord[1]]), color)

    def expose(self, coord: tuple[int, int]):
        """ Sets mask of this node its game board value. """
        self.mask[coord[0]][coord[1]] = self.game[coord[0]][coord[1]]

    def color_change(self, coord: tuple[int, int], color: str):
        """ Wrapper for color cell to also print board and delay graph search. """
        self.color_cell(coord, color)  # for visualization purposes
        self.print_board()  # for visualization purposes
        sleep(GRAPH_SEARCH_DELAY)

    def color_exposed(self, coord: tuple[int, int], color: str):
        """ First exposes node (game board to mask) and changes color. """
        self.expose(coord)
        self.color_cell(coord, color)
        self.color_change(coord, color)

    # def switch_node_color(self, coord: tuple[int, int], color: str):
    #     """ Drops current color and switches to new color, then refreshes. """
    #     self.drop_color(coord)
    #     self.color_change(coord, color)

    def underline_node(self, coord: tuple[int, int]):
        """ Adds underline on top of given node's existing styling, then refreshes board. """
        self.mask[coord[0]][coord[1]] = UNDERLINE + str(self.mask[coord[0]][coord[1]])  # underline the node
        self.print_board()  # refreshes board

    def bold_node(self, coord: tuple[int, int]):
        """ Adds bold on top of given node's existing styling, then refreshes board. """
        self.mask[coord[0]][coord[1]] = BOLD + str(self.mask[coord[0]][coord[1]])  # bolds the node
        self.print_board()  # refreshes board

    # OVERWRITTEN DISPLAY MASK
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
                    continue

                # and continues to regular mask if solver mask was empty there
                tile = self.mask[r][c]
                if tile is False:  # unexplored tile
                    constructed += self.chars['tile']
                elif tile == 0:  # empty tile (zero)
                    constructed += self.chars['zero']
                elif isinstance(tile, int):  # number tile
                    constructed += str(tile)
                elif isinstance(tile, str):  # should only happen if altered by solver for color
                    constructed += tile
                    # print('peepee')

                # this shouldn't activate for a solver display because it would've been caught in the solver mask layer
                else:  # other chars: flag, maybe, etc.
                    constructed += tile
                    # print('poopoo')
                constructed += ' '  # adds space between every character added

            constructed += '\n'  # adds new line at end of the row

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
            self.mask[r][c] = self.color_string(self.chars['mine'], RED)
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
        self.revealed_count = 0

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
