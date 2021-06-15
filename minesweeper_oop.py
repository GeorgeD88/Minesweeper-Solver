from copy import Error
from gameboard import Minesweeper


game = Minesweeper(20, 30, .15)
last = ''
print('\n'*30)

while True:
    print(last + '\n')
    game.display_mask()  # displays game to user
    print('\ninput format: mode row column\nreveal: r | f | m | q')

    try:
        # gets input
        choice_str = input('\n')
        choice = choice_str.split()
        mode = choice.pop(0).lower()
        if mode == 'q':
            break
        row, col = map(int, choice)
        print()

        # input checking to ensure it's within bounds
        while row > game.rows or col > game.cols:
            print('selection out of bounds\n')
            choice = input('\n').split()
            mode = choice.pop(0)
            row, col = map(int, choice)

        # acts on choices (r, f, m, h, q respectively to reveal, flag or flag maybe a tile, to get help or to quit), optionally followed by coordinates
        if mode == 'r':
            # checks if choice was a mine and ends game
            if game.game[row][col] is True:
                game.display_game()
                print('😂'*game.cols)
                print('😂'*game.cols)
                print(' boi you Losttt boiiiiii '.center(game.cols*2, '😂'))
                print('😂'*game.cols)
                print('😂'*game.cols)
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
                if cell_count - count == game.bomb_count:
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
        last = choice_str

        print('\n'*30)

    except Exception as e:
        with open('error.txt', 'w+') as error_file:
            error_file.write(str(e))
        print('💩'*game.cols)
        print('💩'*game.cols)
