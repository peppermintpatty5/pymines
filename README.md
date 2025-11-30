# 💣 pymines

![In-game screenshot of terminal](imgs/screenshot.png)

## About

This is an implementation of the game [Minesweeper](<https://en.wikipedia.org/wiki/Minesweeper_(video_game)>) that uses sets instead of arrays.
As a result of this simple change, the game can progress indefinitely without the need to explicitly resize arrays.

```py
# array logic
if grid[x][y].is_mine:
    ...

# set logic
if (x, y) in coordinates.mines:
    ...
```

Three sets $M, R, F \subset \mathbb{Z^2}$ are used to keep track of the mines, uncovered (revealed) cells, and flags respectively.
Let $A : \mathbb{Z}^2 \to \mathcal{P}(\mathbb{Z}^2)$ be a function which outputs the set of 8 adjacent cells for a given coordinate.

$$A(x, y) = (\{x - 1, x, x + 1\} \times \{y - 1, y, y + 1\}) \setminus \{(x, y)\}$$

### Dynamic generation

On an infinite playing field the mines need to be generated on-the-fly using a _density_ parameter.
The density controls the proportion of cells which are mines.
For a region of width $w$ and height $h$ containing $n$ mines, the density $\delta \in [0, 1]$ is calculated as follows.

$$\delta = \frac{n}{w * h}$$

Each time the player uncovers a cell, mines will be randomly generated in that cell and its adjacent cells with probability $\delta$.
It is critical that no cell undergo random generation twice.
The generation criteria for a cell $(x, y)$ is that it not be uncovered $(x, y) \notin R$ and not be adjacent to any uncovered cells $A(x, y) \cap R = \varnothing$.

As a courtesy, the first cell uncovered will never be a mine.

## Installation

This project requires Python 3.10 or newer and uses only the standard library.
You do not need to install anything else, unless you are on Windows:

> The Windows version of Python doesn't include the [`curses`](https://docs.python.org/3/library/curses.html#module-curses) module.
> A ported version called [UniCurses](https://pypi.org/project/UniCurses) is available.

## Usage

Use the `-h` flag to see the help text.

```sh
python3 -m pymines -h
```

### Controls

|       Key       | Action                       |
| :-------------: | :--------------------------- |
|   Arrow keys    | Move cursor                  |
|      Enter      | Uncover cell at cursor       |
|      Space      | Flag or chord cell at cursor |
| `w` `s` `a` `d` | Scroll window (fine)         |
| `W` `S` `A` `D` | Scroll window (coarse)       |
|       `0`       | Scroll to (0, 0)             |
|       `c`       | Center window to cursor      |
|       `r`       | Refresh window               |
|       `q`       | Quit                         |

Have fun!
