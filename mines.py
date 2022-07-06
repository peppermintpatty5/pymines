"""
Minesweeper
"""

from collections import deque
from enum import Enum
from itertools import product
from random import random


class Tile(Enum):
    """
    A tile uniquely describes a cell. Numeric tiles have corresponding numeric
    values.
    """

    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    PLAIN = 9
    MINE = 10
    DETONATED = 11
    FLAG_RIGHT = 12
    FLAG_WRONG = 13


class Minesweeper:
    """
    An infinite game of minesweeper.
    """

    AUTO_LIMIT = 1 << 16

    def __init__(self, density: float) -> None:
        """
        The density parameter determines what proportion of cells are mines and shall be
        in the range [0, 1].
        """
        self.density = density
        self.mines: set[tuple[int, int]] = set()
        self.uncovered: set[tuple[int, int]] = set()
        self.flags: set[tuple[int, int]] = set()
        self.detonated_count = 0

    @staticmethod
    def adjacent(x: int, y: int) -> set[tuple[int, int]]:
        """
        Return the set of 8 adjacent coordinates.
        """
        return set(product([x - 1, x, x + 1], [y - 1, y, y + 1])) - {(x, y)}

    def uncover(self, x: int, y: int, auto: bool = False) -> bool:
        """
        Uncover the cell at the given coordinate. Return true if the move is legal, false
        otherwise.

        If `auto` is true, then iteratively chord any uncovered 0-tiles. This computation
        can go on indefinitely for low densities, so the number of chords is capped at
        `AUTO_LIMIT`.
        """
        if (x, y) not in self.uncovered and (x, y) not in self.flags:
            # only generate mines after first cell is uncovered
            if self.uncovered:
                for (u, v) in (self.adjacent(x, y) | {(x, y)}) - self.uncovered:
                    if not self.adjacent(u, v) & self.uncovered:
                        if random() < self.density:
                            self.mines.add((u, v))

            # uncover the cell
            self.uncovered.add((x, y))
            if (x, y) in self.mines:
                self.detonated_count += 1

            # automatically chord 0-tiles
            if auto and self.get_tile(x, y) is Tile.ZERO:
                zero_queue = deque([(x, y)])
                zero_cache = {(x, y)}
                chord_count = 0

                while zero_queue and chord_count < Minesweeper.AUTO_LIMIT:
                    zero = zero_queue.popleft()
                    self.chord(*zero)
                    chord_count += 1

                    for (u, v) in self.adjacent(*zero) - zero_cache:
                        if self.get_tile(u, v) is Tile.ZERO:
                            zero_queue.append((u, v))
                            zero_cache.add((u, v))

            return True
        return False

    def flag(self, x: int, y: int) -> bool:
        """
        Set/unset a flag at the given coordinate. A flag precludes a cell from being
        uncovered. Return true if the move is legal, false otherwise.
        """
        if (x, y) not in self.uncovered:
            if (x, y) not in self.flags:
                self.flags.add((x, y))
            else:
                self.flags.remove((x, y))

            return True
        return False

    def chord(self, x: int, y: int, auto: bool = False) -> bool:
        """
        Perform a "chord" move at the given coordinate. Return true if the move is legal,
        false otherwise.
        """
        adj = self.adjacent(x, y)

        if (
            (x, y) in self.uncovered
            and (x, y) not in self.mines
            and len(adj & self.flags) + len(adj & self.uncovered & self.mines)
            == len(adj & self.mines)
        ):
            for (u, v) in adj:
                self.uncover(u, v, auto)

            return True
        return False

    def get_tile(self, x: int, y: int) -> Tile:
        """
        Get the tile associated with the cell at the given coordinate.
        """
        return (
            (
                Tile.DETONATED
                if (x, y) in self.uncovered
                else Tile.FLAG_RIGHT
                if (x, y) in self.flags
                else Tile.MINE
            )
            if (x, y) in self.mines
            else (
                Tile(len(self.adjacent(x, y) & self.mines))
                if (x, y) in self.uncovered
                else Tile.FLAG_WRONG
                if (x, y) in self.flags
                else Tile.PLAIN
            )
        )
