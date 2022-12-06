# interface
import pygame
from gui_game import Minesweeper, Node
from gui_colors import *
from constants import *

# data structures
from collections import deque

# dev stuff
from pprint import PrettyPrinter


pp = PrettyPrinter().pprint  # for dev purposes


class Solver(Minesweeper):

    def __init__(self, rows: int = ROWS, cols: int = COLS, mine_spawn: float or int = MINE_SPAWN, win_height: int = WIN_HEIGHT, win_title: str = WIN_TITLE):
        super().__init__(rows, cols, mine_spawn, win_height, win_title)

        self.first_drop = None
        """ NOTE: going to store the first drop coord in a class variable because we might
        need it a few times and it makes it easier than having to pass it around functions. """

        """ NOTE: when keeping track of certain nodes for a while, like as a class variable,
        store them as coordinates, but when working with the nodes, handle them as node objects. """

        # solver colors
        self.CURRENT = DARK_PURPLE_TINT
        self.VISITED = DARK_YELLOW_TINT
        self.SOLVED = DARK_GREEN_TINT

    """ TODO
    I have to decide how I want to start the solver integration.
    like if I want to be able to continue the solver from wherever the user presses key,
    I have to figure out how I want to grab the existing information.
    or maybe I'll decide to not be able to continue the user's work and I can only activate it
    from the starting empty drop/pool.
    """

    def run_solver(self):
        """ Run solver by initializing bot, then running it. """
        self.init_solver()
        self.solve_board()

    def init_solver(self):
        """ Initialize solver, startup code for bot. """
        self.solved_count = self.flagged_count = 0
        # add solver attributes to every node in the grid
        for node in self.loop_all_nodes():
            node.solved = False
            node.traversed = False  # TODO: not sure if I'll keep this, but this basically turns the yellow coloring into a state too

    # TODO: maybe put init_solver in main solver function and just make it part of the algorithm function.
    def solve_board(self):
        """ Solver algorithm, the whole bot algorithm. """
        # self.init_solver()

        # [0] Random first drop (is done by the player and saved in a class variable)

        # [1] Get starting points for the algorithm (using lake scan)
        """ NOTE: doing old method for now, simply getting nearest chain and ignoring possibilities
        of other chains, which will be handled by lake scan later. """
        nearest_chain = self.find_nearest_chain(self.get_node(*self.first_drop))

        # [2] Loop through islands/starting points and run grind chain at each one.
        """ every time you iterate to the next island and before you run grind chain,
        remember a way to memorize how the chains have expanded in previous chains
        because the next chain might have already been solved because it was expanded into them. """
        # NOTE: also doing old method here and just grinding the chain, when normally we will have a loop of chains
        self.grind_chain(nearest_chain)

    def old_solve(self):
        """ Solver algorithm but I'm just gonna implement the stuff I coded before,
        then I'll move it to the new solver algorithm and plug lake scan into the coord picking.
        drawn out,
               old solve: this is where old solve code is plugged in  ----v
        solving v2: lake scan to get chains, loop through chains and run ***, etcetera etcetera."""
        pass

    # === CHAIN SEARCH ALGORITHMS === NOTE: anything to do with FINDING chains (not solving them), so: find nearest chain, lake scan, even helper functions
    # like mark wall that might be useful because that same code (or at least purpose) is definitely relevant for lake scan.
    def find_nearest_chain(self, start: Node) -> Node:
        """ Uses DFS to find the nearest chain (and returns first node it touched in the chain). """
        stack = deque([(r, c)])  # use append to push, pop to pop
        checked = {(r, c)}  # hashset containing nodes already processed
        self.color_exposed(r, c, GREEN)  # marks the source node green

        while len(stack) > 0:  # while stack not empty
            curr = stack.pop()
            self.color_exposed(*curr, PURPLE)  # sets current node to purple

            if curr not in checked:  # if this node hasn't been checked yet
                # if we hit a number, return its coords
                if self.game[curr[0]][curr[1]] != 0:
                    self.color_exposed(*curr, RED)  # sets destination node to red
                    return curr
                checked.add(curr)

            self.color_exposed(*curr, CYAN)  # sets processed node to cyan

            # checks neighbors
            for adj in self.adjacent_nodes(curr):
                # that means this bumped into an already completed wall
                if not self.bounds(*adj):
                    continue
                if self.is_solved(*adj):
                    input('chick chick, BOOOMMM')
                    return adj
                if adj not in checked and adj not in stack:
                    stack.append(adj)

        # bolds source node and updates display
        self.bold_node(r, c)
        sleep(GRAPH_SEARCH_DELAY)

    def lake_scan(self, start: Node) -> list[Node]:
        """ BFS zero fill from CLI solver could be useful. """
        pass

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

    # === CHAIN SOLVING ALGORITHMS === NOTE: once we have chains, these are algorithms to do with solving them, like follow and grind chain
    def grind_chain(self, r: int, c: int):
        """ Keeps running follow chain on number until the chain is completely solved. """
        last_progress = -1
        total_progress = self.flag_tracker + self.solved_count
        # iter_counter = 1  # DELETE

        # stagnation detector
        while total_progress > last_progress:
            last_progress = total_progress  # current total progress becomes last progress
            self.follow_chain(r, c)
            total_progress = self.flag_tracker + self.solved_count  # current total progress is calculated

            # DELETE --,
            # iter_counter += 1
        # input(f'last progress: {last_progress}\nupdated progress: {total_progress}')
        input('finished grinding chain')

    def follow_chain(self, r: int, c: int):
        """ Follow chain of numbers (using bfs) starting at given coord and process each node. """
        pass

    def simple_solve(self, r: int, c: int) -> bool:
        """ Runs the simple solving algorithm and returns whether tile was solved. """
        pass

    def count_unrevealedNflags(self, r: int, c: int) -> tuple[int, int]:
        # TODO: find a better fucking name to replace this shitty fucking name
        pass

    """ bunch more helpers and small ones like getters:
    is_solved (checks node.solved, which would normally be a function in the node class, but this is only a solver thing so I don't wanna add it in the class definition for nodes in the main game file.)
    determine_if_solved
    is_chain (maybe could make this a node method)
    is_flag (exists as node method already)
    """

    # === COLORING FUNCTIONS === thank fuck I don't have to deal with these like I did in CLI solver,
    # TODO: but I may still need to overwrite some of the update_node/reveal_node functions to instead get the color from the solved state.
    # because the nodes will still have their regular state (like REVEALED & UNREVEALED),
    # but they will need to be colored based on solving. now as for including a traversed attribute, idk if that matters, the node will simply get colored yellow as it's traversed,
    # like a snail trail from the solver, and if it gets solved then it will turn green. but basically the traversed may not need to be an attribute and will simply be a trail from the solver's traversal