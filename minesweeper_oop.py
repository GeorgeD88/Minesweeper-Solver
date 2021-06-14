from gameboard import Minesweeper


game = Minesweeper(30, 50, .15)
game.display_game()
game.display_mask()


# checks if the tile contains a bomb or not
def check_tile(r, c):
    pass

# checks the pressed tile and decides if it's a regular tile and then proceeds as needed
def press(r, c):
    pass
# TODO: do the recursive function for opening a tile surrounded by 0s fro a while

# allows the user to flag unopened tiles as a bomb if speculated to be
def flag(r, c, maybe: bool = False):
    """
        Flags hidden tiles on player's board as surely bomb or possibly a bomb.

        TODO: ARGS
    """

    pass