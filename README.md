# Minesweeper-Solver 💣🧹
**Minesweeper-Solver** is an ever-changing project dedicated to building the most near perfect Minesweeper bot. Minesweeper is a game of numbers and the first 95% of it can be figured out definitively with some basic counting. The real challenge comes during the last bit of the game, where simple counting don't work anymore and you're left with a game of mostly chance. My goal is to design a set of algorithms to play Minesweeper and continuously improve upon these algorithms until the amount of guessing is reduced hopefully to zero. Eventually I will end up with a Minesweeper bot that's basically perfect and can fully solve the board every single time.
## License
**Minesweeper-Solver** is free software, distributed under the terms of the [GNU General Public License, version 3](https://www.gnu.org/licenses/gpl-3.0.html).
## What I Learned
* Graph algorithms such as flood fill, breadth first search, and depth first search
* Memoization
* Creating GUIs with pygame
* Licensing with GNU GPL
<!-- * Linear algebra for solver algorithms -->
## How to Run
The project was originally implemented with a command line interface (CLI), but has been since implemented with a GUI. I provide both versions, but I recommend just running the GUI version.

### Running CLI Versions (deprecated)
In the CLI implementation, the project has 2 parts: the bot and the game itself, spread across 3 files. `cli_game.py` contains the backend of the game (no user input), while `cli_user.py` and `cli_solver.py` each connects the game to their own interface. `cli_user.py` connects the game to a user interface with inputs to allow the user to play, while `cli_solver.py` connects the game to solving algorithms as well as a visualization to show the user what's going on.<br>*The code below can be found in the file `cli_ms.py`.*<br>
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
<img src="https://github.com/GeorgeD88/Minesweeper-Solver/blob/main/img/minesweeper_demo.gif" alt="Minesweeper game CLI demo" width="400">

#### CLI Bot
<img src="https://github.com/GeorgeD88/Minesweeper-Solver/blob/main/img/ms_solver_demo.gif" alt="Minesweeper bot CLI demo" width="400">

### Running GUI Versions
For the GUI implementation on the other hand, I combined the playable version and the solver version into one, spread across 3 files. `gui_game.py` contains the backend/logic of the game (no user input), then `gui_solver.py` adds the solver algorithms to the game, and finally `gui_user.py` adds the user input over everything, allowing you to play the game normally or run the bot to take over at any point. To play: left click to reveal tiles, right click to flag tiles, and press **S** to run the bot<br>*The code below can be found in the file `gui_ms.py`.*<br>
```python
from gui_user import User

# to play Minesweeper
ms = User(20, 30)
ms.play()
```
#### GUI Game
<img src="https://github.com/GeorgeD88/Minesweeper-Solver/blob/main/img/demo_gui_ms.gif" alt="Minesweeper game GUI demo" width="400">

#### GUI Bot
<img src="https://github.com/GeorgeD88/Minesweeper-Solver/blob/main/img/gui_solver_demo.gif" alt="Minesweeper bot GUI demo" width="400">
