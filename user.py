from game import Minesweeper
from textwrap import fill


SPACER = 50  # amount of lines to print to space boards out

class User(Minesweeper):

    def __init__(self, rows: int, cols: int, mine_spawn: float, chars_config: dict = None):
        super().__init__(rows, cols, mine_spawn, chars_config)

    def play(self):
        """ Starts game loop. """
        last_move = ''
        print('\n' * SPACER)

while True:

    try:
        print(last + '\n')
        game.display_mask()  # displays game to user
        print('\ninput format: mode row column\nreveal: R | F | M | Q')

        # gets input
        choice_str = input('\n')
        choice = choice_str.split()
        mode = choice.pop(0).lower()
        if mode == 'q':
            break
        row, col = map(int, choice)
        row -= 1
        col -= 1
        print()

        # input checking to ensure it's within bounds
        while not game.bounds(row, col):
            print('selection out of bounds\n')
            choice = input('\n').split()
            mode = choice.pop(0)
            row, col = map(int, choice)
            row -= 1
            col -= 1


        # acts on choices (r, f, m, h, q respectively to reveal, flag or flag maybe a tile, to get help or to quit), optionally followed by coordinates
        if mode == 'r':
            # checks if choice was a mine and ends game
            if game.game[row][col] is True:
                game.display_game()
                lose_message()
                end_choice = input().lower()
                if end_choice == 'p':
                    pass
                elif end_choice ==
                break
            # if no mine then continue with revealing square
            else:
                game.reveal(row, col)
                cell_count = game.rows * game.cols
                count = 0
                for r in range(game.rows):
                    for c in range(game.cols):
                        if type(game.mask[r][c]) is int:
                            count += 1
                if cell_count - count == game.mine_count:
                    print('\n'*30)
                    game.display_game()
                    print('🅱️'*(game.cols*2))
                    print('🅱️'*(game.cols*2))
                    print(' boi really won like that 😐 '.center(game.cols*2, '🅱'))
                    print('🅱️'*(game.cols*2))
                    print('🅱️'*(game.cols*2))
                    break
        elif mode == 'f':
            game.flag(row, col)
        elif mode == 'm':
            game.maybe(row, col)
        last_move = choice_str

        print('\n'*30)

    except Exception as e:
        with open('error.txt', 'w+') as error_file:
            error_file.write(str(e))
        print('💩'*game.cols)
        print('💩'*game.cols)


def get_options():
    """ Gets game options: rows, columns, and mine probability. """
    options_input = input('format: rows  columns  probability(optional)\n').split()
    return int(options_input[0]), int(options_input[1]), float(options_input[2])

def welcome_message():
    print("""


               ====================================
               === WELCOME TO MINESWEEPER! 💣🧹 ===
               ====================================

                    To get started, input your
             desired dimensions and mine probability.

            """)

def win_message():
    print("""


               ===============
               == YOU WIN!! ==
               ===============

  (P) play again (Q) quit (E) edit settings
            """)

def lose_message():
    print("""


            ===============
            == GAME OVER ==
            ===============

  (P) play again (Q) quit (E) edit settings
            """)


welcome_message()
rows, cols, prob = get_options()
game = Minesweeper(rows, cols, prob)
game.play()