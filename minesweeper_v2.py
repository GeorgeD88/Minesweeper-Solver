#-----------------------------------------------------------------------
# minesweeper.py
#-----------------------------------------------------------------------

import stdio
import stdarray
import sys
import random

# Accept integers rows and cols, and float prob as command-line arguments.
# Create a rows x cols minesweeper game where each cell is a bomb with
# probability prob. Write the rows x cols game and the neighboring bomb counts
# to standard output.

rows = int(input('rows: '))
cols = int(input('columns: '))
prob = float(input('bomb probability: '))

# Create bombs as a rows+2 * cols+2 array.
bombs = stdarray.create2D(rows+2, cols+2, False)

# bombs is [1..rows][1..cols]; the border is used to handle boundary cases.
for r in range(1, rows+1):
    for c in range(1, cols+1):
        bombs[r][c] = (random.random() < prob)

# Write the bombs.
for r in range(1, rows+1):
    for c in range(1, cols+1):
        if bombs[r][c]:
            print('* ')
        else:
            print('. ')
    print()

# Create solution as a rows+2 x cols+2 array.
solution = stdarray.create2D(rows+2, cols+2, 0)

# solution[i][j] is the number of bombs adjacent to cell (i, j).
for r in range(1, rows+1):
    for c in range(1, cols+1):
        # (rr, cc) indexes neighboring cells.
        for rr in range(r-1, r+2):
            for cc in range(c-1, c+2):
                if bombs[rr][cc]:
                    solution[r][c] += 1

# Write solution.
print()
for r in range(1, rows+1):
    for c in range(1, cols+1):
        if bombs[r][c]:
            print('* ')
        else:
            print(str(solution[r][c]) + ' ')
    print()

#-----------------------------------------------------------------------

# python minesweeper.py 3 5 .5
# . . * . *
# * . * . *
# * * * . *
#
# 1 3 * 4 *
# * 6 * 6 *
# * * * 4 *

# python minesweeper.py 3 5 .5
# . . * * .
# . . . * *
# . . . . *
#
# 0 1 * * 3
# 0 1 3 * *
# 0 0 1 3 *
