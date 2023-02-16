from gui_game import Node  # for type hinting only


class DisjointSet:
    """ Disjoint-set data structure implemented with union by rank and path compression.
        The nodes in this case are tuples containing row & column coordinates. """

    def __init__(self):
        self.parent = {}  # keeps track of every node's parent node
        self.rank = {}  # keeps track of every node's rank
        self.representatives = set()  # keeps track of the representatives in the forest
        # self.sizes = {}  # keeps track of the size of every disjoint-set (by representative)
        # TODO: maybe keep track of the sizes of each disjoint-set in the forest
        self.count = 0  # keeps track of the number of disjoint-sets in the forest

    def forest_size(self) -> int:
        """ Returns the number of disjoint-sets in the forest. """
        return self.count

    def exists(self, node: Node) -> bool:
        """ Returns whether given node exists in the forest. """
        return node in self.parent

    def is_representative(self, node: Node) -> bool:
        """ Returns whether given node is a disjoint-set representative. """
        return node in self.representatives

    def get_representatives(self) -> set[Node]:
        """ Returns all the representatives in the disjoint-set forest. """
        return self.representatives

    def new(self, node: Node):
        """ Adds a new node by creating a disjoint-set containing the new node and adding it to the forest. """
        self.parent[node] = node  # sets node's parent to itself (representative)
        self.rank[node] = 0  # initialize node's rank at 0
        self.representatives.add(node)  # new node starts as the representative
        # self.sizes[node] = 1  #  initializes the new disjoint-set's size as 1
        self.count += 1  # increment count of disjoint-sets in the forest

    # path compression
    def find(self, node: Node) -> Node:
        """ Find and return the representative of the given node's disjoint set. """
        # follow parent pointer until you reach the representative of the set
        if self.parent[node] != node:
            # sets the node's parent to the representative, compressing the path
            self.parent[node] = self.find(self.parent[node])
        return self.parent[node]

    # union by rank
    def union(self, nodeA: Node, nodeB: Node) -> bool:
        """ Performs union on the disjoint-sets of the given nodes and returns whether the union was successful. """
        reprA, reprB = self.find(nodeA), self.find(nodeB)  # gets each node's representative

        # if they're the same representative then they're already part of the same disjoint-set
        if reprA == reprB:
            return False  # union was unsuccessful
        # merge into A's disjoint-set because it has higher rank
        elif self.rank[reprA] > self.rank[reprB]:
            self.parent[reprB] = reprA  # B.parent -> A
            self.representatives.remove(reprB)  # B loses representative status
            # self.sizes[reprA] += self.sizes[reprB]  # combine B's size to A
            # self.sizes.pop(reprB)  # remove B's size because it's no longer a representative
        # merge into B's disjoint-set because it has higher rank
        elif self.rank[reprB] > self.rank[reprA]:
            self.parent[reprA] = reprB # A.parent -> B
            self.representatives.remove(reprA)  # A loses representative status
            # self.sizes[reprB] += self.sizes[reprA]  # combine A's size to B
            # self.sizes.pop(reprA)  # remove B's size because it's no longer a representative
        # if they have equal rank, merge into A's disjoint-set and increase its rank
        else:
            self.parent[reprB] = reprA  # B.parent -> A
            self.representatives.remove(reprB)  # B loses representative status
            self.rank[reprA] += 1
            # self.sizes[reprA] += self.sizes[reprB]  # combine B's size to A
            # self.sizes.pop(reprB)  # remove B's size because it's no longer a representative

        self.count -= 1  # decrement the number of disjoint-sets
        return True  # union was successful
