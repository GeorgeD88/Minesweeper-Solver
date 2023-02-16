# interface
import pygame
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
        self.first_drop = None

        # solver colors
        self.CURRENT = DARK_PURPLE_TINT
        self.LAKE = DULL_BLUE
        self.VISITED = YELLOW_TINT  # visited but wasn't able to solve
        self.SOLVED = GREEN_TINT
        # colors that represent revealed state but are not specifically REVEALED state
        self.revealed_states = {self.CURRENT, self.VISITED, self.SOLVED, self.REVEALED, BORDER_BLUE, DARK_RED_TINT, SOFT_BLUE}

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

    # TODO: maybe put init_solver in main solver function and just make it part of the algorithm function.
    def solve_board(self):
        """ Solver algorithm, the whole bot algorithm. """
        # [0] Random first drop (is done by the player and saved in a class variable)
        first_node = self.get_node(*self.first_drop)

        # [1] Get starting points for the algorithm (using lake scan)
        chains = self.lake_scan(first_node)  # run initial lake scan

        # list the chains found
        print(f'found {len(chains)} chains:')
        for chain in chains:
            print(str(chain.get_coord()), end=', ')
        print('\n')

        # [2] Loop through chains/starting points and run grind chain at each one.
        for chain in chains:
            print('grinding:', str(chain.get_coord()))
            self.switch_color(chain, SOFT_BLUE)  # mark chain's starting point
            self.delay(2)
            self.grind_chain(chain)

    # === CHAIN SEARCH ALGORITHMS ===
    # like mark wall that might be useful because that same code (or at least purpose) is definitely relevant for lake scan.
    # def find_nearest_chain(self, start: Node) -> Node:
    #     """ Uses DFS to find the nearest chain (and returns first node it touched in the chain). """
    #     stack = deque([start])  # use append to push, pop to pop
    #     discovered = {start}  # hashset containing nodes already discovered

    #     while len(stack) > 0:
    #         curr = stack.pop()

    #         self.switch_color(curr, self.LAKE)

    #         # add adjacent nodes to stack
    #         for adj in self.adjacent_nodes(curr):
    #             if adj.is_chain():  # chain was found
    #                 return adj
    #             elif adj not in discovered:
    #                 stack.append(adj)
    #                 discovered.add(adj)

    def union_adjacent_chain(self, DSU: DisjointSet, node: Node):
        """ Perform union on the given node and its adjacent chain nodes. """
        for adj in self.adjacent_nodes(node):  # iterate adjacent nodes
            if self.is_revealed_solver(adj) and adj.is_chain():  # if chain and revealed
                # add adjacent node to the structure first if it's not in it
                if not DSU.exists(adj):
                    DSU.new(adj)
                # sets adjacent node's color to dark red tint if the node was not already part of the same set
                if DSU.union(node, adj):
                    self.switch_color(adj, DARK_RED_TINT)

    def lake_scan(self, start: Node) -> set[Node]:
        """ lake scan implemented with disjoint sets. """
        DSU = DisjointSet()  # disjoint-set data structure
        queue = deque([start])  # append to enqueue and popleft to dequeue
        discovered = {start}  # hashset keeping track of already discovered nodes

        while len(queue) > 0:
            curr = queue.popleft()

            # when border is hit, union node with adjacent chain tiles
            if curr.value != 0:
                # if node not in disjoint-set, add it to the structure
                if not DSU.exists(curr):
                    DSU.new(curr)
                    self.switch_color(curr, BORDER_BLUE)  # set chain tile to border blue
                self.union_adjacent_chain(DSU, curr)  # union this node with its adjacent chain tiles
                continue
            # else it's a still an empty/lake node, so just color it
            else:
                self.switch_color(curr, self.LAKE)
                self.solver_delay(0.008)

            # add adjacent nodes to the queue
            for adj in self.adjacent_nodes(curr):
                if adj not in discovered:
                    queue.append(adj)
                    discovered.add(adj)

        # return disjoint-set representatives (each is a reference to an island)
        return DSU.get_representatives()
        # return DSU

    # - Removed lake scan BFS implementation to the side, might need trace chain from it -

    def lake_scan_later(self, start: Node) -> set[Node]:
        """ TODO: implement lake scan for later stages where some of the chains
        you scan might already be touched/solved. This would be a change in the lake fill step,
        where when you hit the edge chains that contain the lakes, you don't add them to the all nodes list
        but you still use them as the nodes that stop you from searching farther. """
        DSU: DisjointSet = self.lake_scan(start)
        if DSU.count == 1:
            return set()  # return empty set indicating no new chains
        DSU.representatives.remove(start)

    # === CHAIN SOLVING ALGORITHMS ===
    def grind_chain(self, chain_start: Node):
        """ Keeps running follow chain until the chain stagnates. """
        last_progress = -1
        curr_progress = self.flagged_count + self.solved_count

        # stagnation detector
        while curr_progress > last_progress:
            last_progress = curr_progress  # current total progress becomes last progress
            self.follow_chain(chain_start)  # follow chain
            curr_progress = self.flagged_count + self.solved_count  # current total progress is calculated

    def follow_chain(self, chain_start: Node):
        """ Follow chain of numbers (using bfs) starting at given coord and process each node. """
        queue = deque([chain_start])  # use append to enqueue, popleft to dequeue
        discovered = {chain_start}  # hashset containing nodes already discovered

        while len(queue) > 0:
            curr = queue.popleft()

            self.switch_color(curr, self.CURRENT)

            """ when processing a node, we will be traversing nodes that have been processed before
            in past calls of the follow chain function. those nodes may or may not have been fully solved.
            so first we have to check for that before we try to solving. """

            # process node
            if curr.is_solved() is False:
                """ NOTE: note that, this tile could've been solved by the actions of a tile next to it
                but not marked as solved, so make note of that and try to include that when considering efficiency. """
                solve_result = self.simple_solve(curr)
                # color node green if was solved, else make it yellow
                self.switch_color(curr, self.SOLVED if solve_result else self.VISITED)
            else:
                self.switch_color(curr, self.SOLVED)
                # color it back to green, because remember it was colored purple at the beginning of the iteration

            # add adjacent nodes to queue
            for adj in self.adjacent_nodes(curr):
                # node is revealed and a chain tile
                if self.is_revealed_solver(adj) and adj.is_chain() and adj not in discovered:
                    queue.append(adj)
                    discovered.add(adj)

    def simple_solve(self, node: Node) -> bool:
        """ Runs the simple solving algorithm and returns whether tile was solved. """
        unrevealed_count, flag_count = self.count_unrevealedNflags(node)
        mines_left = node.value - flag_count  # mines actually left to find

        # if the mines left match the unrevealed count, then we're able to solve the tile
        if mines_left == unrevealed_count:
            # if they're both 0, then the tile was solved but not marked, meaning it was solved because of actions of adjacent tiles
            if mines_left == 0:
                node.solved = True
                self.solved_count += 1
                return True
            # flags all unrevealed tiles, as they have to be mines
            for adj in self.adjacent_nodes(node):
                if adj.is_unrevealed():  # if unrevealed, flag it
                    self.flag(adj)
                    self.flagged_count += 1
        # no more mines or flags left, so reveal the rest of the tiles
        elif mines_left == 0:
            for adj in self.adjacent_nodes(node):
                if adj.is_unrevealed():  # if unrevealed, reveal it
                    self.reveal(adj)
        # not enough information to solve the tile
        else:
            return False

        # tile was able to solve, returns True
        node.solved = True
        self.solved_count += 1
        return True

    # TODO: find a better name ASAP
    def count_unrevealedNflags(self, node: Node) -> tuple[int, int]:
        """ Returns count of adjacent flags and unrevealed tiles. """
        unrevealed_count = flagged_count = 0

        for adj in self.adjacent_nodes(node):
            if adj.is_unrevealed():
                unrevealed_count += 1
            elif adj.is_flagged():
                flagged_count += 1

        return unrevealed_count, flagged_count

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

    # === COLORING FUNCTIONS === thank fuck I don't have to deal with these like I did in CLI solver,
    def switch_color(self, node: Node, new_color: str):
        """ Switches node's color, redraws, updates display, and delays solver. """
        node.state = new_color
        self.update_revealed(node)
        self.solver_delay()  # NOTE: this feels odd to include, it feels dirty like cli solver
