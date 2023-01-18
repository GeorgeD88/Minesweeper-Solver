class DSU:
    """ Disjoint-set data structure implemented with union by rank and path compression.
        The nodes in this case are tuples containing row & column coordinates. """

    def __init__(self):
        self.parent = {}  # keeps track of every node's parent node
        self.rank = {}  # keeps track of every node's rank
        # TODO: maybe keep track of the sizes of each disjoint-set in the forest
        self.count = 0  # keeps track of the number of disjoint-sets in the forest

    def forest_size(self) -> int:
        """ Returns the number of disjoint-sets in the forest. """
        return self.count

    def exists(self, node: tuple[int, int]) -> bool:
        """ Returns whether node exists in the forest. """
        return node in self.parent

    def new(self, node: tuple[int, int]):
        """ Adds a new node by creating a disjoint-set containing the new node and adding it to the forest. """
        self.parent[node] = node  # sets node's parent to itself (representative)
        self.rank[node] = 0  # initialize node's rank at 0
        self.count += 1  # increment count of disjoint-sets in the forest

    # path compression
    def find(self, node: tuple[int, int]) -> tuple[int, int]:
        """ Find and return the representative of the given node's disjoint set. """
        # follow parent pointer until you reach the representative of the set
        if self.parent[node] != node:
            # sets the node's parent to the representative, compressing the path
            self.parent[node] = self.find(self.parent[node])
        return self.parent[node]

    # union by rank
    def union(self, nodeA: tuple[int, int], nodeB: tuple[int, int]) -> bool:
        """ Performs union on the disjoint-sets of the given nodes and returns whether the union was successful. """
        reprA, reprB = self.find(nodeA), self.find(nodeB)  # gets each node's representative

        # if they're the same representative then they're already part of the same disjoint-set
        if reprA == reprB:
            return False  # union was unsuccessful
        # merge into A's disjoint-set because it has higher rank
        elif self.rank[reprA] > self.rank[reprB]:
            self.parent[reprB] = reprA  # B.parent -> A
        # merge into B's disjoint-set because it has higher rank
        elif self.rank[reprB] > self.rank[reprA]:
            self.parent[reprA] = reprB # A.parent -> B
        # if they have equal rank, merge into A's disjoint-set and increase its rank
        else:
            self.parent[reprB] = reprA  # B.parent -> A
            self.rank[reprA] += 1

        self.count -= 1  # decrement the number of disjoint-sets
        return True  # union was successful
