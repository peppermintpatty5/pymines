"""
Command-line interface for minesweeper game.
"""

import argparse
import curses
import signal

from . import textui
from .mines import Minesweeper


if __name__ == "__main__":
    # suppress SIGINT
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    parser = argparse.ArgumentParser(
        prog="pymines",
        description="Play an unending game of minesweeper",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-d",
        "--density",
        help="The percentage of cells that are mines."
        " A higher value corresponds to a harder game.",
        type=float,
        default=17.0,
    )
    parser.add_argument(
        "-l",
        "--lives",
        help="The number of detonations allowed before all mine locations are revealed."
        " Enter a negative value for unlimited lives.",
        type=int,
        default=1,
    )
    args = parser.parse_args()

    game = Minesweeper(args.density / 100)
    curses.wrapper(textui.main, game, args.lives)
