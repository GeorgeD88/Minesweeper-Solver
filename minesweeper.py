from http.client import ImproperConnectionState


import solver
import user



# Minesweeper w/ user
user.play()  # user(game)

# Minesweeper w/ bot
solver.play()  # solver(game)