#!/usr/bin/env python3

"""
Command-line interface for minesweeper game.
"""

import argparse
import curses
import signal

import textui
from mines import Minesweeper


if __name__ == "__main__":
    # suppress SIGINT
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    parser = argparse.ArgumentParser(
        description="Play a game of minesweeper",
    )
    parser.add_argument(
        "-d",
        "--density",
        help="the proportion of cells that are mines, default is 0.17",
        type=float,
        default=0.17,
    )
    parser.add_argument(
        "-l",
        "--lives",
        help="default is 1 life, negative values are treated as infinity",
        type=int,
        default=1,
    )
    args = parser.parse_args()

    game = Minesweeper(args.density)
    curses.wrapper(textui.main, game, args.lives)
