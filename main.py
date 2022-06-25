#!/usr/bin/env python3

"""
Command-line interface for minesweeper game.
"""

import argparse
import curses
import signal

from mines import Minesweeper
from textui import TextUI


if __name__ == "__main__":
    # suppress SIGINT
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    parser = argparse.ArgumentParser(
        description="Play a game of minesweeper",
    )
    parser.add_argument(
        "-d",
        "--density",
        help="determines what proportion of cells are mines, default 0.17",
        type=float,
        default=0.17,
    )
    parser.add_argument(
        "-x",
        "--x-ray",
        help="enables X-ray cheats",
        action="store_true",
        dest="x_ray",
    )
    args = parser.parse_args()

    game = Minesweeper(args.density)
    curses.wrapper(TextUI.main, game, x_ray=args.x_ray)
