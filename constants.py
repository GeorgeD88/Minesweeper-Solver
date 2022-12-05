""" This is store global constants that are used among all Minesweeper files. """

WIN_TITLE = 'Minesweeper 💣🧹'
FLAG_STR = '='

# == BOARD PROPERTIES ==
ROWS = 25
COLS = 40
# TODO: implement a mine probability vs mine count option
MINE_SPAWN = 0.15  # probability of mines spawning
# MINE_SPAWN = 99  # number of mines

# == NODE STATES/COLORS ==
""" starred lines are colors that are also used to represent a state
GRID_LINE: color of the lines between tiles
TILE_NUMBER: color of the number/text on tiles, aka foreground color
REVEALED: color of revealed tiles, aka background color                     *
UNREVEALED: color of unrevealed tiles                                       *
MINE: color of tiles that are mines                                         *?
FLAG: color of unrevealed tiles that are flagged                            *
"""

# == FRONTEND CONSTANTS ==
WIN_HEIGHT = 900  # window height
WAIT = 0.03  # in seconds

# == BACKEND CONSTANTS ==
ADJACENT_COORDS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
