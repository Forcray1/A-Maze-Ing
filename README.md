*This project has been created as part of the 42 curriculum by \<mlorenzo\>,<elsahin\> .*

# A-Maze-Ing

## Description

A-Maze-Ing is a terminal maze generator written in Python. The program reads a configuration file, procedurally generates a maze using a **Depth-First Search (DFS)** algorithm, displays it in the terminal, and lets the player navigate it interactively. An automatic solver based on **BFS (Breadth-First Search)** is also available to compute and display the shortest path from entry to exit.

The project is structured in several independent modules:

- `mazegen/` — standalone reusable maze generator (installable via pip)
- `core/` — maze solver and configuration validator
- `cli/` — ASCII rendering and interactive menu
- `game/` — player logic and gameplay session

---

## Instructions

- You can use the command 'make run', wich will start with the asked command : python3 a_maze_ing config.txt
- Or if you want to enter a different config file, or test the arguments error gestion, directly enter it in the terminal with this format : python3 a_maze_ing [config file]

### Requirements

- Python 3.10+
- No external dependencies (standard library only)

### Build the reusable `mazegen` package

```bash
make build
# Produces mazegen-1.0.0-py3-none-any.whl and mazegen-1.0.0.tar.gz at the root
```

---

## Configuration File

The program takes a plain text configuration file as its only argument. Each line follows the format `KEY=VALUE`. Lines starting with `#` are treated as comments and ignored.

| Key | Type | Required | Description | Example |
|---|---|---|---|---|
| `WIDTH` | `int` | ✅ | Width of the maze (number of columns) | `WIDTH=20` |
| `HEIGHT` | `int` | ✅ | Height of the maze (number of rows) | `HEIGHT=15` |
| `ENTRY` | `x,y` | ✅ | Entry coordinates (0-indexed). `x` = WIDTH or `y` = HEIGHT is clamped to the last cell. | `ENTRY=0,0` |
| `EXIT` | `x,y` | ✅ | Exit coordinates. Same rules as ENTRY. | `EXIT=19,14` |
| `OUTPUT_FILE` | `string` | ✅ | Path to the output `.txt` file for the hex dump. | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | `True`/`False` | ✅ | If `True`, generates a perfect maze (unique path). If `False`, extra openings are added. | `PERFECT=True` |
| `SHOW_PROGRESS` | `True`/`False` | ❌ | Animates maze generation step by step. Defaults to `False`. | `SHOW_PROGRESS=False` |
| `SEED` | `int` | ❌ | Random seed for reproducible generation. If omitted, a random 64-bit seed is used. | `SEED=42` |

Example `config.txt`:

```
WIDTH=20
HEIGHT=20
ENTRY=0,0
EXIT=20,20
OUTPUT_FILE=maze.txt
PERFECT=True
SHOW_PROGRESS=False
```

---

## Maze Generation Algorithm

The maze is generated using **iterative Depth-First Search (DFS)**, implemented without recursion via an explicit stack.

### How it works

1. Start from the entry cell and push it onto the stack.
2. Pick a random unvisited neighbour, carve a passage to it, mark it visited, and push it.
3. If no unvisited neighbours exist, backtrack by popping the stack.
4. Repeat until the stack is empty — every cell has been visited exactly once.

### Why DFS?

- **Perfect mazes by default**: DFS guarantees exactly one path between any two cells, producing a maze with no loops and no isolated regions — matching the `PERFECT=True` requirement.
- **Simple and efficient**: O(n) time and space where n is the number of cells.
- **Long, winding corridors**: DFS tends to produce mazes with long, challenging passages, which makes for a more engaging player experience.
- **Trivial reproducibility**: The only randomness is in neighbour selection, so fixing a seed entirely reproduces the maze.

---

## Reusable Module — mazegen

The `mazegen` package (`mazegen/maze_maker.py`) is fully standalone and has no external dependencies. It can be imported and used in any Python 3.8+ project independently of this file.

### What is reusable

- `MazeGenerator` class — generates any rectangular maze with configurable size, entry/exit, seed, and mode (perfect or imperfect).
- The bitmask grid format is self-contained and straightforward to consume in any renderer or solver.

### Install from the pre-built package

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Build from scratch (evaluation)

```bash
python -m venv venv
source venv/bin/activate
pip install build
python -m build
# or simply:
make build
```

### Instantiation and basic example

```python
from mazegen.maze_maker import MazeGenerator

# Create a 10×10 maze, starting at (0, 0) and ending at (9, 9)
gen = MazeGenerator(
    width=10,
    height=10,
    entry=(0, 0),
    exit_point=(9, 9),
)

# Generate the maze — returns a 2-D list of bitmasks
grid = gen.generate()
```

### Custom parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `width` | `int` | — | Width of the maze |
| `height` | `int` | — | Height of the maze |
| `entry` | `tuple[int, int]` | — | Entry point `(x, y)` |
| `exit_point` | `tuple[int, int]` | — | Exit point `(x, y)` |
| `perfect` | `bool` | `True` | No loops if `True`, extra openings if `False` |
| `print_42` | `bool` | `False` | Embeds a "42" logo as blocked cells (width ≥ 7, height ≥ 5) |
| `seed` | `int \| None` | `None` | Random seed for reproducible generation |

```python
# Reproducible 20×20 maze with a fixed seed
gen = MazeGenerator(
    width=20,
    height=20,
    entry=(0, 0),
    exit_point=(19, 19),
    perfect=True,
    seed=1337,
)
grid = gen.generate()
```

### Accessing the generated structure

`generate()` returns a 2-D list `grid[y][x]` of integer bitmasks representing open walls:

| Constant | Value | Meaning |
|---|---|---|
| `N` | `1` | North wall is open |
| `S` | `2` | South wall is open |
| `E` | `4` | East wall is open |
| `W` | `8` | West wall is open |
| `BLOCK` | `16` | Cell is blocked (impassable) |

```python
from mazegen.maze_maker import MazeGenerator, N, E

gen = MazeGenerator(width=5, height=5, entry=(0, 0), exit_point=(4, 4), seed=0)
grid = gen.generate()

cell = grid[3][2]   # cell at x=2, y=3
if cell & N:
    print("North passage is open")
if cell & E:
    print("East passage is open")
```

### Accessing a solution

Pass the generated grid to `solver_maze()` from `core/solver.py` (BFS). It returns the shortest path as a move string (`N`, `S`, `E`, `W`):

```python
from mazegen.maze_maker import MazeGenerator
from core.solver import solver_maze

gen = MazeGenerator(width=10, height=10, entry=(0, 0), exit_point=(9, 9), seed=42)
grid = gen.generate()

config = {"WIDTH": 10, "HEIGHT": 10, "ENTRY": "0,0", "EXIT": "9,9"}
moves = solver_maze(config, grid)
print("Solution:", moves)   # e.g. "SSEENN..."
```

---

### Planning

We planned to separate the work between us by letting mlorenzo doing the brut algorithms for the maze generator and solver, while elsahin did all the interactive interface. Once that done we put our work together, explained each other the logic and reflexion used, and the both of us worked on the bonus together.

### What worked well / what could be improved

Everything went well, the work has been separated equally, and we did our parts efficiently, and within the deadlines that we setted up. The sharing of our work could have been improved, as it took some time to undesrtand the code of the other one, and adapt it to something the both of us were happy with.

### Bonus

As bonus, we added an animation while the maze is creating itself, wich speed can be adapted, We added the possibility to change the color of the 42 logo as well as the walls. And finally we also added a game, wich make the actual maze playable, with some stats about the score you did on this maze, as well as some easter eggs.

### Tools used

- Python 3.10
- `flake8` for linting
- `mypy` for static type checking
- `pytest` for unit tests
- `build` / `setuptools` for packaging
- `git` to share our progress and final project

---

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Depth-First Search — Wikipedia](https://en.wikipedia.org/wiki/Depth-first_search)
- [Breadth-First Search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Python `random` module documentation](https://docs.python.org/3/library/random.html)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/)
- [mypy documentation](https://mypy.readthedocs.io/)

### AI usage

AI was strictely used as a learning tool, to do repetitive task, such as type hints, and to clarify the subject
