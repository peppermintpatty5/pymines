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

    def uncover(self, x: int, y: int) -> bool:
        """
        Uncover the cell at the given coordinate. Return true if the move is legal, false
        otherwise.
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

            return True
        return False

    def auto_uncover(self, x: int, y: int) -> bool:
        """
        Uncover the cell at the given coordinate and iteratively uncover cells adjacent
        to 0-tiles. This computation can go on indefinitely for low densities, so the
        number of cells uncovered is capped at `AUTO_LIMIT`.

        Return true if the move is legal, false otherwise.
        """
        num_uncovered = 0
        queue = deque([(x, y)])  # queue ordered by proximity
        cache = {(x, y)}  # avoid queueing the same thing twice

        while queue and num_uncovered < Minesweeper.AUTO_LIMIT:
            (x, y) = queue.popleft()
            adj = self.adjacent(x, y)

            if self.uncover(x, y) and (x, y) not in self.mines and not adj & self.mines:
                num_uncovered += 1
                for (u, v) in adj:
                    if (
                        (u, v) not in cache
                        and (u, v) not in self.uncovered
                        and (u, v) not in self.flags
                    ):
                        queue.append((u, v))
                        cache.add((u, v))

        return num_uncovered > 0

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
                if auto:
                    self.auto_uncover(u, v)
                else:
                    self.uncover(u, v)

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
