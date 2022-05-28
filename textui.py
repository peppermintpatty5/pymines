"""
Text user interface
"""

import curses

from mines import Minesweeper


class TextUI:
    """
    Text user interface.
    """

    @staticmethod
    def tile_char(tile: Minesweeper.Tile) -> str:
        """
        Maps each tile to a character representation.
        """
        match tile:
            case Minesweeper.Tile.ZERO:
                char = " "
            case Minesweeper.Tile.ONE:
                char = "1"
            case Minesweeper.Tile.TWO:
                char = "2"
            case Minesweeper.Tile.THREE:
                char = "3"
            case Minesweeper.Tile.FOUR:
                char = "4"
            case Minesweeper.Tile.FIVE:
                char = "5"
            case Minesweeper.Tile.SIX:
                char = "6"
            case Minesweeper.Tile.SEVEN:
                char = "7"
            case Minesweeper.Tile.EIGHT:
                char = "8"
            case Minesweeper.Tile.PLAIN:
                char = "-"
            case Minesweeper.Tile.MINE:
                char = "*"
            case Minesweeper.Tile.DETONATED:
                char = "@"
            case Minesweeper.Tile.FLAG_RIGHT:
                char = "#"
            case Minesweeper.Tile.FLAG_WRONG:
                char = "X"
            case _:
                raise ValueError("unknown tile")

        return char

    @staticmethod
    def tile_attr(tile: Minesweeper.Tile) -> int:
        """
        Maps each tile to an attribute which can be used directly in `attrset`.
        """
        match tile:
            case (
                Minesweeper.Tile.ONE
                | Minesweeper.Tile.THREE
                | Minesweeper.Tile.SEVEN
                | Minesweeper.Tile.EIGHT
                | Minesweeper.Tile.PLAIN
                | Minesweeper.Tile.MINE
                | Minesweeper.Tile.DETONATED
                | Minesweeper.Tile.FLAG_RIGHT
                | Minesweeper.Tile.FLAG_WRONG
            ):
                return curses.color_pair(tile.value + 1) | curses.A_BOLD
            case (
                Minesweeper.Tile.ZERO
                | Minesweeper.Tile.TWO
                | Minesweeper.Tile.FOUR
                | Minesweeper.Tile.FIVE
                | Minesweeper.Tile.SIX
            ):
                return curses.color_pair(tile.value + 1) | curses.A_NORMAL
            case _:
                return curses.color_pair(0)

    @staticmethod
    def confirm_yn(window: curses.window, message: str) -> bool:
        """
        Prompts the user for yes/no confirmation with the given message. Returns true if
        the user chose "yes", false if the user chose "no".
        """
        max_y, _ = window.getmaxyx()

        window.move(max_y - 1, 0)
        window.clrtoeol()
        window.insstr(f"{message} [y/n]", curses.color_pair(0))
        curses.curs_set(0)

        while True:
            match window.get_wch():
                case "y" | "Y":
                    return True
                case "n" | "N":
                    return False

    @staticmethod
    def start(game: Minesweeper, x_ray=False) -> None:
        """
        Starts an ncurses user interface for the minesweeper game.
        """
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.use_default_colors()
        stdscr.keypad(True)
        stdscr.clear()

        tile_hide = {
            Minesweeper.Tile.MINE: Minesweeper.Tile.PLAIN,
            Minesweeper.Tile.FLAG_WRONG: Minesweeper.Tile.FLAG_RIGHT,
        }
        tile_fg_map = {
            Minesweeper.Tile.ZERO: curses.COLOR_WHITE,
            Minesweeper.Tile.ONE: curses.COLOR_BLUE,
            Minesweeper.Tile.TWO: curses.COLOR_GREEN,
            Minesweeper.Tile.THREE: curses.COLOR_RED,
            Minesweeper.Tile.FOUR: curses.COLOR_BLUE,
            Minesweeper.Tile.FIVE: curses.COLOR_RED,
            Minesweeper.Tile.SIX: curses.COLOR_CYAN,
            Minesweeper.Tile.SEVEN: curses.COLOR_WHITE,
            Minesweeper.Tile.EIGHT: curses.COLOR_BLACK,
            Minesweeper.Tile.PLAIN: curses.COLOR_BLACK,
            Minesweeper.Tile.MINE: curses.COLOR_MAGENTA,
            Minesweeper.Tile.DETONATED: curses.COLOR_MAGENTA,
            Minesweeper.Tile.FLAG_RIGHT: curses.COLOR_GREEN,
            Minesweeper.Tile.FLAG_WRONG: curses.COLOR_MAGENTA,
        }
        for tile, fg in tile_fg_map.items():
            curses.init_pair(tile.value + 1, fg, -1)

        ax, ay = 0, 0  # anchor point, top left corner
        cx, cy = 0, 0  # cursor point, relative to anchor

        while True:
            max_y, max_x = stdscr.getmaxyx()

            # print the grid
            curses.curs_set(0)
            for y in range(max_y):
                for x in range(max_x // 2):
                    tile = game.get_tile(ax + x, ay + y)
                    if not x_ray:
                        tile = tile_hide.get(tile, tile)
                    try:
                        stdscr.addch(
                            y, x * 2 + 1, TextUI.tile_char(tile), TextUI.tile_attr(tile)
                        )
                    except curses.error:
                        pass

            stdscr.move(cy, cx * 2 + 1)
            stdscr.refresh()
            curses.curs_set(1)

            match stdscr.get_wch():
                case "w":
                    ay -= 1
                case "s":
                    ay += 1
                case "a":
                    ax -= 1
                case "d":
                    ax += 1
                case "W":
                    ay -= 5
                case "S":
                    ay += 5
                case "A":
                    ax -= 5
                case "D":
                    ax += 5
                case curses.KEY_UP:
                    if cy - 1 < 0:
                        ay -= 1
                    else:
                        cy -= 1
                case curses.KEY_DOWN:
                    if cy + 1 >= max_y:
                        ay += 1
                    else:
                        cy += 1
                case curses.KEY_LEFT:
                    if cx - 1 < 0:
                        ax -= 1
                    else:
                        cx -= 1
                case curses.KEY_RIGHT:
                    if cx + 1 >= max_x // 2:
                        ax += 1
                    else:
                        cx += 1
                case "0":
                    max_y, max_x = stdscr.getmaxyx()
                    ax, ay = -max_x // 4, -max_y // 2
                    cx, cy = max_x // 4, max_y // 2
                case curses.KEY_ENTER | "\r" | "\n":
                    game.auto_uncover(ax + cx, ay + cy)
                case " ":
                    if not game.flag(ax + cx, ay + cy):
                        game.chord(ax + cx, ay + cy, auto=True)
                case "r" | "R":
                    stdscr.clear()
                    stdscr.refresh()
                case "q" | "Q":
                    if TextUI.confirm_yn(stdscr, "Quit?"):
                        break
                    stdscr.clear()

        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
