"""
Minesweeper
"""

from enum import Enum
from itertools import product
from random import random


class Minesweeper:
    """
    An infinite game of minesweeper.
    """

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

    def __init__(self, density: float) -> None:
        self.density = density
        self.mines: set[tuple[int, int]] = set()
        self.uncovered: set[tuple[int, int]] = set()
        self.flags: set[tuple[int, int]] = set()

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

            return True
        return False

    def flag(self, x: int, y: int) -> bool:
        """
        Set/unset the cell at the given coordinate. Return true if the move is legal,
        false otherwise.
        """
        if (x, y) not in self.uncovered:
            if (x, y) not in self.flags:
                self.flags.add((x, y))
            else:
                self.flags.remove((x, y))

            return True
        return False

    def chord(self, x: int, y: int) -> bool:
        """
        Perform a "chord" move at the given coordinate. Return true if the move is legal,
        false otherwise.
        """
        adj = self.adjacent(x, y)

        if (x, y) in self.uncovered and len(adj & self.flags) + len(
            adj & self.uncovered & self.mines
        ) == len(adj & self.mines):
            for (u, v) in adj:
                self.uncover(u, v)

            return True
        return False

    def get_tile(self, x: int, y: int) -> Tile:
        """
        Get the tile associated with the cell at the given coordinate
        """
        if (x, y) in self.mines:
            if (x, y) in self.uncovered:
                tile = Minesweeper.Tile.DETONATED
            elif (x, y) in self.flags:
                tile = Minesweeper.Tile.FLAG_RIGHT
            else:
                tile = Minesweeper.Tile.MINE
        else:
            if (x, y) in self.uncovered:
                tile = Minesweeper.Tile(len(self.adjacent(x, y) & self.mines))
            elif (x, y) in self.flags:
                tile = Minesweeper.Tile.FLAG_WRONG
            else:
                tile = Minesweeper.Tile.PLAIN

        return tile
