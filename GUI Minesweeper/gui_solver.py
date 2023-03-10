# interface
import pygame
import ptext
from gui_game import Minesweeper, Node
from gui_colors import *
from constants import *

# data structures
from disjoint_set import DisjointSet
from collections import deque

# dev stuff
from pprint import PrettyPrinter


pp = PrettyPrinter().pprint  # for dev purposes


class Solver(Minesweeper):

    def __init__(self, rows: int = ROWS, cols: int = COLS, mine_spawn: float or int = MINE_SPAWN, win_height: int = WIN_HEIGHT, win_title: str = WIN_TITLE):
        super().__init__(rows, cols, mine_spawn, win_height, win_title)
        self.first_drop = None  # keeps track of user's initial drop (that's where solving will start)

        # solver colors
        self.CURRENT = WHITE #DARK_PURPLE_TINT
        self.LAKE = DULL_BLUE
        self.VISITED = YELLOW_TINT  # visited but wasn't able to solve
        self.SOLVED = GREEN_TINT
        # colors that represent revealed state but are not specifically REVEALED state
        self.revealed_states = {self.CURRENT, self.VISITED, self.SOLVED, self.REVEALED, BORDER_BLUE, DARK_RED_TINT, SOFT_BLUE}

    # === MAIN SOLVER CODE ===
    def init_solver(self):
        """ Initialize solver, startup code for bot. """
        self.solved_count = self.flagged_count = 0
        # add solved attribute to every node in the grid
        for node in self.loop_all_nodes():
            node.solved = False

    def solve_board(self):
        """ Solver algorithm, the whole bot algorithm. """
        self.init_solver()  # initialize values

        # [0] Random first drop (performed by the player and saved in a class variable)
        initial_drop = self.get_node(*self.first_drop)


        # [1] Get starting points for the algorithm (using lake scan)
        # use append to enqueue, popleft to dequeue
        self.chain_queue = deque(self.lake_scan(initial_drop))  # run initial lake scan and queue chains to solve
        self.stagnated_queue = deque()  # keeps track of stagnated chains

        # list the chains found
        print(f'\nfound {len(self.chain_queue)} chains:', end=' ')
        for chain in self.chain_queue:
            print(str(chain.get_coord()), end=', ')
        print()


        # [2] While the queue of chains is not empty, pop and grind the next chain
        while len(self.chain_queue) > 0:
            chain = self.chain_queue.popleft()  # pop chain to grind

            # visuals
            print('\ngrinding:', str(chain.get_coord()), '\n')
            self.switch_color(chain, SOFT_BLUE)  # mark chain's starting point
            self.delay(0.3)

            grind_result = self.grind_chain(chain)  # run grind chain
            # if chain was not fully solved (stagnated) add to stagnated queue
            if not grind_result:
                self.stagnated_queue.append(chain)
                print('\nchain stagnated:', str(chain.get_coord()), '\n')


        # [3] Use pattern recognition to break stagnated chains 😈
        # list the chains that stagnated
        print(f'\n{len(self.stagnated_queue)} stagnated chains:', end=' ')
        for chain in self.stagnated_queue:
            print(str(chain.get_coord()), end=', ')
        print()
        pass

        print('finished solve cycle')


    # === LAKE SCAN ===
    def lake_scan(self, start: Node, border: Node = None) -> tuple[Node, set[Node]]:
        """ Lake scan implemented with disjoint sets. """
        DSU = DisjointSet()  # disjoint-set data structure
        queue = deque([start])  # append to enqueue and popleft to dequeue
        discovered = {start}  # hashset keeping track of already discovered nodes

        while len(queue) > 0:
            curr = queue.popleft()

            # border is hit, union node with adjacent chain tiles
            if curr.value != 0:
                # if node not in disjoint-set, add it to the structure
                if not DSU.exists(curr):
                    DSU.new(curr)
                    self.switch_color(curr, BORDER_BLUE)  # set chain tile to border blue
                self.union_adjacent_chain(DSU, curr)  # union this node with its adjacent chain tiles
                continue  # don't adjacent tiles, can't traverse past border
            # else it's a still an empty/lake node, so just color it and continue
            else:
                self.switch_color(curr, self.LAKE)
                self.solver_delay(0.004)

            # add adjacent nodes to the queue
            for adj in self.adjacent_nodes(curr):
                if adj not in discovered:
                    queue.append(adj)
                    discovered.add(adj)

        # return disjoint-set representatives (each is a reference to a chain)
        if border is None:  # no border specified, return chains as-is
            return DSU.get_representatives()
        else:  # if border is given, remove it from the chains before returning
            repr = DSU.get_representatives()  # get representatives
            repr.remove(DSU.find(border))  # remove border chain
            return repr  # return representatives

    def union_adjacent_chain(self, DSU: DisjointSet, node: Node):
        """ Perform union on the given node and its adjacent chain nodes. """
        for adj in self.adjacent_nodes(node):  # iterate adjacent nodes
            if self.is_revealed_solver(adj) and adj.is_chain():  # if chain and revealed
                # add adjacent node to the structure first if it's not in it
                if not DSU.exists(adj):
                    DSU.new(adj)
                # attempt to union current node with adjacent node
                if DSU.union(node, adj):
                    # sets adjacent node's color to dark red tint if union was successful
                    self.switch_color(adj, DARK_RED_TINT)


    # === CHAIN SOLVING ===
    def grind_chain(self, chain_start: Node) -> bool:
        """ Keeps running solve chain until the chain stagnates. """
        # initialize progress trackers for every iteration to detect stagnation
        last_progress, curr_progress = -1, self.flagged_count + self.solved_count

        # record current solved count before grinding chain
        initial_solved_count = self.solved_count

        # run solve chain until progress stagnates
        while curr_progress > last_progress:
            last_progress = curr_progress  # current total progress becomes last progress
            self.solve_chain(chain_start)  # solve chain
            curr_progress = self.flagged_count + self.solved_count  # new total progress is calculated

        newly_solved = self.solved_count - initial_solved_count  # calculate number of newly solved tiles
        chain_length = self.measure_chain(chain_start)  # calculate total number of tiles in chain

        # returns whether the chain was fully solved by comparing chain's solved count with the chain's total count
        return newly_solved == chain_length

    def solve_chain(self, chain_start: Node):
        """ Follows chain of tiles and simple solves each one. """
        queue = deque([chain_start])  # use append to enqueue, popleft to dequeue
        discovered = {chain_start}  # hashset containing nodes already discovered

        while len(queue) > 0:
            curr = queue.popleft()

            self.switch_color(curr, self.CURRENT)

            """ NOTE: when processing a node, we will be traversing nodes that have been processed before
            in past calls of the follow chain function. those nodes may or may not have been fully solved.
            so first we have to check for that before we try to solving. """

            # check if tile is not yet solved
            if curr.is_solved() is False:
                """ NOTE: note that, this tile could've been solved by the actions of a tile next to it
                but not marked as solved, so make note of that and try to include that when considering efficiency. """
                # color node green if was able to solve, else make it yellow
                if self.simple_solve(curr):
                    self.switch_color(curr, self.SOLVED)
                # if node was not solved, make it yellow and add number of real mines left
                else:
                    self.switch_unsolved(curr, self.VISITED)

            else:
                # color back to green (because it was colored purple at the start of the iteration)
                self.switch_color(curr, self.SOLVED)

            # add adjacent nodes to queue
            for adj in self.adjacent_nodes(curr):
                # add adj node if it's revealed and a chain tile
                if self.is_revealed_solver(adj) and adj.is_chain() and adj not in discovered:
                    queue.append(adj)
                    discovered.add(adj)

    def simple_solve(self, node: Node) -> bool:
        """ Runs the simple solving algorithm and returns whether tile was solved. """
        # count surrounding unrevealed tiles and flags
        unrevealed_count, flag_count = self.count_adjacent_tiles(node)

        # mine count minus flag count is equal to mines actually left to find
        mines_left = node.value - flag_count

        # if the mines left match the unrevealed count, then they're all mines so flag them
        if mines_left == unrevealed_count:
            # if they're both 0, then the tile was solved but not marked
            # (meaning it was solved because of actions of adjacent tiles)
            if mines_left == 0:
                node.solved = True
                self.solved_count += 1
                return True
            # flags all unrevealed tiles, as they have to be mines
            self.flag_adjacent_nodes(node)
        # no more mines or flags left, so reveal the rest of the tiles
        elif mines_left == 0:
            self.reveal_adjacent_nodes(node)
        # not enough information to solve the tile
        else:
            return False

        # if tile was able to solve, returns True
        node.solved = True
        self.solved_count += 1
        return True

    # === CHAIN SOLVING HELPERS ===
    def measure_chain(self, chain_start: Node) -> int:
        """ Follow chains and counts number of tiles. """
        queue = deque([chain_start])  # use append to enqueue, popleft to dequeue
        discovered = {chain_start}  # hashset containing nodes already discovered
        tile_count = 0

        while len(queue) > 0:
            curr = queue.popleft()
            tile_count += 1  # increase tile count

            # add adjacent nodes to queue
            for adj in self.adjacent_nodes(curr):
                # add adj node if it's revealed and a chain tile
                if self.is_revealed_solver(adj) and adj.is_chain() and adj not in discovered:
                    queue.append(adj)
                    discovered.add(adj)

        return tile_count

    def count_adjacent_tiles(self, node: Node) -> tuple[int, int]:
        """ Returns count of adjacent flags and unrevealed tiles. """
        unrevealed_count = flagged_count = 0

        # go through adjacent nodes
        for adj in self.adjacent_nodes(node):
            if adj.is_unrevealed():  # increment unrevealed counter
                unrevealed_count += 1
            elif adj.is_flagged():  # increment flagged counter
                flagged_count += 1

        return unrevealed_count, flagged_count

    def reveal_adjacent_nodes(self, node: Node):
        """ Reveals all adjacent unrevealed tiles. """
        for adj in self.adjacent_nodes(node):
            # if not unrevealed, skip
            if not adj.is_unrevealed():
                continue
            self.reveal(adj)  # reveal node first
            # check if lake is found and scan
            if not adj.is_empty():  # is not lake, no need to scan
                continue

            # lake is found, scan and add new chains to chain queue
            new_chains = self.lake_scan(adj, border=node)
            if len(new_chains) > 0:
                print(f'found {len(new_chains)} new chains')
                self.chain_queue.extend(new_chains)  # add newly discovered chains to the chain queue
            self.delay(0.03)

    def flag_adjacent_nodes(self, node: Node):
        """ Flags all adjacent unrevealed tiles. """
        for adj in self.adjacent_nodes(node):
            if adj.is_unrevealed():  # if unrevealed, flag it
                self.flag(adj)
                self.flagged_count += 1


    # === BREAKING STAGNATION ===
    # def find_stagnation/search_stagnation??

    # === HELPER FUNCTIONS ===
    def solver_delay(self, wait: float = SOLVER_WAIT):
        """ Delay some amount of time, for animation/visual purposes. """
        pygame.time.delay(int(wait*1000))

    def is_revealed_solver(self, node: Node):
        """ Checks if revealed but also considers solver revealed states. """
        return node.state in self.revealed_states

    def determine_if_solved(self, node: Node) -> bool:
        """ Calculates if the node is solved by checking the adjacent nodes. """
        for adj in self.adjacent_nodes(node):
            # aborts immediately if any adjacent node is unrevealed
            if adj.is_unrevealed():
                return False
        return True

    # === COLORING FUNCTIONS ===
    def switch_color(self, node: Node, new_color: str):
        """ Switches node's color, redraws, updates display, and delays solver. """
        node.state = new_color
        self.update_revealed(node)

    def switch_unsolved(self, node: Node, new_color: str):
        """ Switch color and updates revealed but modified specifically for an unsolved node. """
        node.state = new_color
        self.draw_unsolved(node)
        self.update_display()

    def draw_unsolved(self, node: Node):
        """ Draws revealed nodes that are unsolved (draws "real" mine count). """
        self.draw_node(node)  # draws tile color, aka bg
        self.draw_node_grid(node)  # draws grid lines
        # NOTE: if unsolved then it should always not be empty
        # if not node.is_empty():  # draws number if value over 0
        self.draw_real_mine_count(node)  # draws tile number, aka fg

    def draw_real_mine_count(self, node: Node):
        """ Draws node's real mine count onto pygame window. """
        # calculate real mine count
        flag_count = self.count_adjacent_tiles(node)[1]
        real_mine_count = node.value - flag_count

        # draw the value
        ptext.draw(str(real_mine_count), centerx=node.x+self.cell_size//2, centery=node.y+self.cell_size//2, fontsize=int(self.cell_size/4*3), color=DARK_GRAY)#3:2
