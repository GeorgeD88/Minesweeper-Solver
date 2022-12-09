# Minesweeper-Solver 💣🧹
**Minesweeper-Solver** is an ever-changing project dedicated to building the most near perfect Minesweeper bot. Minesweeper is a game of numbers and the first 90% of it can be figured out definitively with some basic calculations. The real challenge comes with the last bit of the game where those simple calculations don't work anymore and you're left with a game of mostly chance. My goal is to write a combination of algorithms to solve the game and continuously add to and improve these algorithms to reduce having to rely on chance as much as possible. Eventually I will end up with a Minesweeper bot that's near perfect at playing the game and I no longer have to tap and pray to finish off the board.
## License
**Minesweeper-Solver** is free software, distributed under the terms of the [GNU General Public License, version 3](https://www.gnu.org/licenses/gpl-3.0.html).
## What I Learned
* Graph algorithms such as flood fill, breadth first search, and depth first search
* Memoization
* Creating GUIs with pygame
* Displaying matrices in the command line
* Licensing with GNU GPL
<!-- * Linear algebra for solver algorithms -->
## How to Run
The project was originally implemented with a command line interface (CLI), but is currently in the process of being implemented with a GUI. I've converted the game's logic and user interface to use a GUI, yet still have to convert the solver to work in the GUI.

### Running CLI Versions (deprecated)
The project has 2 parts, the game itself and the bot, spread across 3 files. `cli_game.py` contains the backend of the game (no user input), while `cli_user.py` and `cli_solver.py` each connects the game to their own interface. `cli_user.py` connects the game to a user interface with inputs to allow the user to play, while `cli_solver.py` connects the game to solving algorithms as well as a visualization to show the user what's going on.<br>*The code below can be found in the file `cli_ms.py`.*<br>
```python
import cli_user
import cli_solver

# to play Minesweeper
game = cli_user.init_game()
game.play()  # user + game

# to watch the bot play Minesweeper
bot = cli_solver.init_solver()
bot.solve()  # solver + game
```
#### CLI Game
<img src="https://github.com/GeorgeD88/Minesweeper-Solver/blob/main/minesweeper_demo.gif" alt="Minesweeper game CLI demo" width="400">

#### CLI Bot
<img src="https://github.com/GeorgeD88/Minesweeper-Solver/blob/main/ms_solver_demo.gif" alt="Minesweeper bot CLI demo" width="400">

### Running GUI Versions
The solver component is currently not ready in the GUI version, but the game itself is ready to play. To play the game, import the class `User` from the module `gui_user.py`, initialize it, and run the method `.play()`. You can initialize the `User` object with different parameters if you want to change the board dimensions, number of mines, etc. Set the mine spawn to a value below 1 to generate mines by probability, or a value over 1 to generate mines by number of mines.<br>*The code below can be found in the file `gui_ms.py`.*<br>
```python
from gui_user import User

# to play Minesweeper
ms = User()
ms.play()
```
#### GUI Game
<img src="https://github.com/GeorgeD88/Minesweeper-Solver/blob/main/demo_gui_ms.gif" alt="Minesweeper game GUI demo" width="400">

#### GUI Bot
<img src="https://github.com/GeorgeD88/Minesweeper-Solver/blob/main/gui_solver_demo.gif" alt="Minesweeper bot GUI demo" width="400">
