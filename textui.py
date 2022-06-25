"""
Text user interface
"""

import curses

from mines import Minesweeper, Tile


class TextUI:
    """
    Text user interface.
    """

    @staticmethod
    def tile_char(tile: Tile) -> str:
        """
        Maps each tile to a character representation.
        """
        match tile:
            case Tile.ZERO:
                char = " "
            case Tile.ONE:
                char = "1"
            case Tile.TWO:
                char = "2"
            case Tile.THREE:
                char = "3"
            case Tile.FOUR:
                char = "4"
            case Tile.FIVE:
                char = "5"
            case Tile.SIX:
                char = "6"
            case Tile.SEVEN:
                char = "7"
            case Tile.EIGHT:
                char = "8"
            case Tile.PLAIN:
                char = "-"
            case Tile.MINE:
                char = "*"
            case Tile.DETONATED:
                char = "@"
            case Tile.FLAG_RIGHT:
                char = "#"
            case Tile.FLAG_WRONG:
                char = "X"
            case _:
                raise ValueError("unknown tile")

        return char

    @staticmethod
    def tile_attr(tile: Tile) -> int:
        """
        Maps each tile to an attribute which can be used directly in `attrset`.
        """
        match tile:
            case (
                Tile.ONE
                | Tile.THREE
                | Tile.SEVEN
                | Tile.EIGHT
                | Tile.PLAIN
                | Tile.MINE
                | Tile.DETONATED
                | Tile.FLAG_RIGHT
                | Tile.FLAG_WRONG
            ):
                return curses.color_pair(tile.value + 1) | curses.A_BOLD
            case (Tile.ZERO | Tile.TWO | Tile.FOUR | Tile.FIVE | Tile.SIX):
                return curses.color_pair(tile.value + 1) | curses.A_NORMAL
            case _:
                return curses.color_pair(0)

    @staticmethod
    def confirm_yn(window: curses.window, message: str) -> bool:
        """
        Prompts the user for yes/no confirmation with the given message. Returns true if
        the user chose "yes", false if the user chose "no".
        """
        max_y, max_x = window.getmaxyx()

        curses.init_pair(
            50, curses.COLOR_BLACK, curses.COLOR_YELLOW
        )  # TODO better pair number
        window.insstr(
            max_y - 1,
            0,
            f"{message} [y/n]".ljust(max_x),
            curses.color_pair(50),
        )
        curses.curs_set(0)

        while True:
            match window.get_wch():
                case "y" | "Y":
                    return True
                case "n" | "N":
                    return False

    @staticmethod
    def print_status_bar(window: curses.window, x: int, y: int) -> None:
        """
        Print status bar showing cursor location and possibly other information.
        """
        max_y, max_x = window.getmaxyx()

        curses.init_pair(51, curses.COLOR_BLACK, curses.COLOR_WHITE)
        window.insstr(
            max_y - 1,
            0,
            f"{(x, y)}".ljust(max_x),
            curses.color_pair(51),
        )

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
            Tile.MINE: Tile.PLAIN,
            Tile.FLAG_WRONG: Tile.FLAG_RIGHT,
        }
        tile_fg_map = {
            Tile.ZERO: curses.COLOR_WHITE,
            Tile.ONE: curses.COLOR_BLUE,
            Tile.TWO: curses.COLOR_GREEN,
            Tile.THREE: curses.COLOR_RED,
            Tile.FOUR: curses.COLOR_BLUE,
            Tile.FIVE: curses.COLOR_RED,
            Tile.SIX: curses.COLOR_CYAN,
            Tile.SEVEN: curses.COLOR_WHITE,
            Tile.EIGHT: curses.COLOR_BLACK,
            Tile.PLAIN: curses.COLOR_BLACK,
            Tile.MINE: curses.COLOR_MAGENTA,
            Tile.DETONATED: curses.COLOR_MAGENTA,
            Tile.FLAG_RIGHT: curses.COLOR_GREEN,
            Tile.FLAG_WRONG: curses.COLOR_MAGENTA,
        }
        for tile, fg in tile_fg_map.items():
            curses.init_pair(tile.value + 1, fg, -1)

        ax, ay = 0, 0  # anchor point, bottom left corner
        cx, cy = 0, 0  # cursor point, relative to anchor

        while True:
            max_y, max_x = stdscr.getmaxyx()
            max_cx, max_cy = max_x // 2, max_y - 1

            TextUI.print_status_bar(stdscr, ax + cx, ay + cy)

            # print the grid
            curses.curs_set(0)
            for y in range(max_cy):
                for x in range(max_cx):
                    tile = game.get_tile(ax + x, ay + y)
                    if not x_ray:
                        tile = tile_hide.get(tile, tile)
                    try:
                        stdscr.addch(
                            max_y - 2 - y,
                            x * 2 + 1,
                            TextUI.tile_char(tile),
                            TextUI.tile_attr(tile),
                        )
                    except curses.error:
                        pass

            stdscr.move(max_y - 2 - cy, cx * 2 + 1)
            stdscr.refresh()
            curses.curs_set(1)

            match stdscr.get_wch():
                case "w":
                    ay += 1
                case "s":
                    ay -= 1
                case "a":
                    ax -= 1
                case "d":
                    ax += 1
                case "W":
                    ay += 5
                case "S":
                    ay -= 5
                case "A":
                    ax -= 5
                case "D":
                    ax += 5
                case curses.KEY_UP:
                    if cy + 1 >= max_cy:
                        ay += 1
                    else:
                        cy += 1
                case curses.KEY_DOWN:
                    if cy - 1 < 0:
                        ay -= 1
                    else:
                        cy -= 1
                case curses.KEY_LEFT:
                    if cx - 1 < 0:
                        ax -= 1
                    else:
                        cx -= 1
                case curses.KEY_RIGHT:
                    if cx + 1 >= max_cx:
                        ax += 1
                    else:
                        cx += 1
                case "0":
                    ax, ay = -(max_cx // 2), -(max_cy // 2)
                    cx, cy = max_cx // 2, max_cy // 2
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
                    stdscr.erase()

        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()
