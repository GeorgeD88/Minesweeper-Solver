# Minesweeper-Solver
**Minesweeper-Solver** is a ever-changing project dedicated to building the most near perfect Minesweeper bot. Minesweeper is a game of numbers and the first 80% of it can be figured out definitively with some basic calculations. The real challenge comes with the last bit of the game where those simple calculations don't work anymore and you're left with a game of mostly chance. My goal is to write a combination of algorithms to solve the game and continuously add to and improve them to reduce the game of chance as much as possible. Eventually I will end up with a Minesweeper bot that's near perfect at playing the game and I no longer have to tap and pray to finish off the board.
## License
**Minesweeper-Solver** is free software, distributed under the terms of the [GNU General Public License, version 3](https://www.gnu.org/licenses/gpl-3.0.html).
## How to Run
The project has 2 parts, the game itself and the bot, spread across 3 files. `game.py` contains the backend of the game (no user input), while `user.py` and `solver.py` each connects the game to their own user interface. `user.py` connects the game to a user interface with inputs to allow the user to play, while `solver.py` connects the game to solving algorithms as well as a user interface (without inputs) to show the user what's going on.<br>
_NOTE: solver.py is currently being built and so far doesn't have anything to start with_<br>
```python
import user
import solver

# Minesweeper game
game = user.init_game()
game.play()  # user + game

# Minesweeper bot
bot = solver.init_solver()
bot.solve()  # solver + game
```