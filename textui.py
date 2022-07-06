"""
Text user interface
"""

import curses

from mines import Minesweeper, Tile


class TextUI:
    """
    Text user interface.
    """

    TILE_CHAR = {
        Tile.ZERO: " ",
        Tile.ONE: "1",
        Tile.TWO: "2",
        Tile.THREE: "3",
        Tile.FOUR: "4",
        Tile.FIVE: "5",
        Tile.SIX: "6",
        Tile.SEVEN: "7",
        Tile.EIGHT: "8",
        Tile.PLAIN: "-",
        Tile.MINE: "*",
        Tile.DETONATED: "@",
        Tile.FLAG_RIGHT: "#",
        Tile.FLAG_WRONG: "X",
    }
    TILE_COLORS = {
        Tile.ZERO: (curses.COLOR_WHITE, False),
        Tile.ONE: (curses.COLOR_BLUE, True),
        Tile.TWO: (curses.COLOR_GREEN, False),
        Tile.THREE: (curses.COLOR_RED, True),
        Tile.FOUR: (curses.COLOR_BLUE, False),
        Tile.FIVE: (curses.COLOR_RED, False),
        Tile.SIX: (curses.COLOR_CYAN, False),
        Tile.SEVEN: (curses.COLOR_WHITE, True),
        Tile.EIGHT: (curses.COLOR_BLACK, True),
        Tile.PLAIN: (curses.COLOR_BLACK, True),
        Tile.MINE: (curses.COLOR_MAGENTA, False),
        Tile.DETONATED: (curses.COLOR_YELLOW, True),
        Tile.FLAG_RIGHT: (curses.COLOR_GREEN, True),
        Tile.FLAG_WRONG: (curses.COLOR_MAGENTA, True),
    }

    @staticmethod
    def init_colors() -> None:
        """
        Initialize colors for user interface.
        """
        curses.use_default_colors()

        for tile, (fg, _) in TextUI.TILE_COLORS.items():
            curses.init_pair(tile.value + 1, fg, -1)

        curses.init_pair(50, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(51, curses.COLOR_BLACK, curses.COLOR_WHITE)

    @staticmethod
    def tile_attr(tile: Tile) -> int:
        """
        Maps each tile to an attribute which can be used directly in `attrset`.
        """
        _, bold = TextUI.TILE_COLORS[tile]

        return curses.color_pair(tile.value + 1) | (
            curses.A_BOLD if bold else curses.A_NORMAL
        )

    @staticmethod
    def confirm_yn(window: curses.window, message: str) -> bool:
        """
        Prompts the user for yes/no confirmation with the given message. Returns true if
        the user chose "yes", false if the user chose "no".
        """
        max_y, max_x = window.getmaxyx()

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
                case _:
                    pass

    @staticmethod
    def print_grid(
        stdscr: curses.window, game: Minesweeper, ax: int, ay: int, x_ray: bool
    ) -> None:
        """
        Print grid to screen.
        """
        tile_hide = {
            Tile.MINE: Tile.PLAIN,
            Tile.FLAG_WRONG: Tile.FLAG_RIGHT,
        }

        max_y, max_x = stdscr.getmaxyx()
        max_cx, max_cy = max_x // 2, max_y - 1

        for y in range(max_cy):
            for x in range(max_cx):
                tile = game.get_tile(ax + x, ay + y)
                if not x_ray and game.detonated_count < 1:
                    tile = tile_hide.get(tile, tile)
                stdscr.addstr(
                    max_y - 2 - y,
                    x * 2,
                    " " + TextUI.TILE_CHAR[tile],
                    TextUI.tile_attr(tile),
                )

    @staticmethod
    def print_status_bar(window: curses.window, x: int, y: int) -> None:
        """
        Print status bar showing cursor location and possibly other information.
        """
        max_y, max_x = window.getmaxyx()

        window.insstr(
            max_y - 1,
            0,
            f"{(x, y)}".ljust(max_x),
            curses.color_pair(51),
        )

    @staticmethod
    def main(stdscr: curses.window, game: Minesweeper, x_ray: bool = False) -> None:
        """
        Entry point for graphical minesweeper game. Call this function using
        `curses.wrapper`.
        """
        TextUI.init_colors()
        stdscr.clear()

        ax, ay = 0, 0  # anchor point, bottom left corner
        cx, cy = 0, 0  # cursor point, relative to anchor

        while True:
            max_y, max_x = stdscr.getmaxyx()
            max_cx, max_cy = max_x // 2, max_y - 1

            TextUI.print_status_bar(stdscr, ax + cx, ay + cy)
            TextUI.print_grid(stdscr, game, ax, ay, x_ray)

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
                    game.uncover(ax + cx, ay + cy, auto=True)
                case " ":
                    if not game.flag(ax + cx, ay + cy):
                        game.chord(ax + cx, ay + cy, auto=True)
                case "r" | "R":
                    stdscr.clear()
                    stdscr.refresh()
                case "q" | "Q":
                    if TextUI.confirm_yn(stdscr, "Quit?"):
                        return
                    stdscr.erase()
