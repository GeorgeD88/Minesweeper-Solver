import random
import sys


# Accept integers rows and cols, and float prob as command-line arguments.
# Create a rows x cols minesweeper game where each cell is a bomb with
# probability prob. Write the rows x cols game and the neighboring bomb counts
# to standard output.

rows = int(input('rows: '))
cols = int(input('columns: '))
prob = float(input('bomb probability: '))

# initializes a 2d array to hold the bombs as a rows+2 * cols+2 array,
# each element being a boolean for a bomb existing or not (False as default for now).
bombs = [[False for i in range(cols+2)] for j in range(rows+2)]

# goes through every individual element in the bomb array and runs a random number to determine whether
# or not to insert a bomb there; the bomb is inserted if the number is within the given probability.
# OLD COMMENT: bombs is [1..rows][1..cols]; the border is used to handle boundary cases.
for r in range(1, rows+1):
    for c in range(1, cols+1):
        bombs[r][c] = (random.random() < prob)

# initializes a 2d array to hold the solution board as a rows+2 * cols+2 array,
# each regular tile contains the number of adjacent tiles with bombs.
solution = [[0 for i in range(cols+2)] for j in range(rows+2)]

# goes through every element and replaces every regular
# tile with the number of bombs in the adjacent tiles.
for r in range(1, rows+1):
    for c in range(1, cols+1):
        # (rr, cc) indexes neighboring cells.
        for rr in range(r-1, r+2):
            for cc in range(c-1, c+2):
                if bombs[rr][cc]:
                    solution[r][c] += 1


# # prints the initial state of the board with just the bombs and regular tiles
# for r in range(1, rows+1):
#     for c in range(1, cols+1):
#         if bombs[r][c]:
#             print('* ', end="")
#         else:
#             print('. ', end="")
#     print()

# prints the solution of the board with the number tiles and exposed bombs
# print()
# for r in range(1, rows+1):
#     for c in range(1, cols+1):
#         if bombs[r][c]:
#             print('* ', end="")
#         else:
#             print(str(solution[r][c]) + ' ', end="")
#     print()

game = [[False for i in range(cols+2)] for j in range(rows+2)]


# checks if the tile contains a bomb or not
def check_tile(r, c):
    pass

# checks the pressed tile and decides if it's a regular tile and then proceeds as needed
def press(r, c):
    pass
# TODO: do the recursive function for opening a tile surrounded by 0s fro a while

# allows the user to flag unopened tiles as a bomb if speculated to be
def flag(r, c):
    pass