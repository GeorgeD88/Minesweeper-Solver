import cli_solver_cleaned
import user


# Minesweeper game
# game = user.init_game()
# game.play()  # user + game

# Minesweeper bot
bot = cli_solver_cleaned.init_solver()
bot.solve()  # solver + game