from copy import Error
from gameboard import Minesweeper


game = Minesweeper(20, 30, .15)
last = ''
print('\n'*30)

while True:
    # GAME =====
    print(last + '\n')
    game.display_mask()  # displays game to use
    # ==========

    """
    Realistically, a user won't have access to the code the same way as a solver can just copy the game.mask
    data for example, but that doesn't matter. The solver being able to access the game.mask for example is
    just the solver's way of interpreting the data/that's how the solver is able to process it (idk you get it).
    The point is it doesn't matter, I'm still giving the solver the same data presented to the user, but in the
    code form it actually understands instead of as lines of strings like a user would see. What's important
    is that I'm writing algorithms to actually traverse and solve the grid, the solver having access to the code
    form of the board is merely the data input/transfer method, basically how it gets the data. In the future
    I can create an AI that would be able to look at the grid presented to it and actually process the data that way,
    but the data it gets is no different so that doesn't matter and that's just a waste of time.
                        $$$ Anyways, heres' my master piece, enjoy B) $$$
    """

    # data transfer, pulling data from game to solver
    choice_str = input('\n')
    choice = choice_str.split()
    mode = choice.pop(0).lower()
    if mode == 'q':
        break
    row, col = map(int, choice)
    print()

    game.reveal(row, col)
    cell_count = game.rows * game.cols
    count = 0
    for r in range(game.rows):
        for c in range(game.cols):
            if type(game.mask[r][c]) is int:
                count += 1
    if cell_count - count == game.bomb_count:
        print('\n'*30)
        game.display_game()
        print('🅱️'*(game.cols*2))
        print('🅱️'*(game.cols*2))
        print(' boi really won like that 😐 '.center(game.cols*2, '🅱'))
        print('🅱️'*(game.cols*2))
        print('🅱️'*(game.cols*2))
        break

    print('\n'*30)

    # except Exception as e:
    #     with open('error.txt', 'w+') as error_file:
    #         error_file.write(str(e))
    #     print('💩'*game.cols)
    #     print('💩'*game.cols)
