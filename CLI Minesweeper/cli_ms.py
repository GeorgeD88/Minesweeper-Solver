import cli_user
import cli_solver

# to play Minesweeper
game = cli_user.init_game()
game.play()  # user + game

# to watch the bot play Minesweeper
bot = cli_solver.init_solver()
bot.solve()  # solver + game
