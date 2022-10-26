import cli_solver
import user


# Minesweeper game
# game = user.init_game()
# game.play()  # user + game

# Minesweeper bot
bot = cli_solver.init_solver()
bot.solve()  # solver + game