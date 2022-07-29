"""
Text user interface
"""

import curses

from mines import Minesweeper, Tile


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


def init_colors() -> None:
    """
    Initialize color pairs for 8 basic colors.
    """
    curses.use_default_colors()

    for color in range(8):
        curses.init_pair(color + 1, color, -1)


def get_color(fg: int, bold: bool) -> int:
    """
    Return the attribute value for displaying text in the specified foreground color on
    the default background color.
    """
    return curses.color_pair(fg + 1) | (curses.A_BOLD if bold else curses.A_NORMAL)


class TextUI:
    """
    Text user interface.
    """

    def __init__(self, stdscr: curses.window, game: Minesweeper, lives: int) -> None:
        self.stdscr = stdscr
        self.game = game
        self.lives = lives
        self.ax, self.ay = (0, 0)
        self.cx, self.cy = (0, 0)

    def scroll_by(self, x: int, y: int) -> None:
        """
        Scroll window by given offset.
        """
        self.ax += x
        self.ay += y

    def scroll_to(self, x: int, y: int) -> None:
        """
        Scroll window to given location.
        """
        old_x, old_y = self.cursor_location()
        self.scroll_by(x - old_x, y - old_y)

    def cursor_location(self) -> tuple[int, int]:
        """
        Get the absolute location `(x, y)` of the cursor.
        """
        return (self.ax + self.cx, self.ay + self.cy)

    def move_cursor(self, x: int, y: int) -> None:
        """
        Move cursor by given offset, scrolling the window to keep the cursor in bounds.
        """
        max_y, max_x = self.stdscr.getmaxyx()
        max_cx = max_x // 2
        max_cy = max_y - 1

        self.cx += x
        self.cy += y

        if self.cx < 0:
            self.ax += self.cx
            self.cx = 0
        if self.cy < 0:
            self.ay += self.cy
            self.cy = 0
        if self.cx >= max_cx:
            self.ax += self.cx - max_cx + 1
            self.cx = max_cx - 1
        if self.cy >= max_cy:
            self.ay += self.cy - max_cy + 1
            self.cy = max_cy - 1

    def center_cursor(self) -> None:
        """
        Adjust window and relative cursor location so that the cursor is centered within
        the window. The absolute cursor location will not change.
        """
        max_y, max_x = self.stdscr.getmaxyx()
        max_cx = max_x // 2
        max_cy = max_y - 1

        dx = max_cx // 2 - self.cx
        dy = max_cy // 2 - self.cy

        self.cx += dx
        self.cy += dy
        self.ax -= dx
        self.ay -= dy

    def confirm_yn(self, message: str) -> bool:
        """
        Prompts the user for yes/no confirmation with the given message. Returns true if
        the user chose "yes", false if the user chose "no".
        """
        max_y, max_x = self.stdscr.getmaxyx()

        self.stdscr.insstr(
            max_y - 1,
            0,
            f" {message} [y/n]".ljust(max_x),
            get_color(curses.COLOR_YELLOW, False) | curses.A_REVERSE,
        )
        curses.curs_set(0)

        while True:
            match self.stdscr.get_wch():
                case "y" | "Y":
                    return True
                case "n" | "N":
                    return False
                case _:
                    pass

    def print_grid(self) -> None:
        """
        Print grid to screen.
        """
        tile_hide = {
            Tile.MINE: Tile.PLAIN,
            Tile.FLAG_WRONG: Tile.FLAG_RIGHT,
        }

        max_y, max_x = self.stdscr.getmaxyx()
        max_cx, max_cy = max_x // 2, max_y - 1

        for y in range(max_cy):
            for x in range(max_cx):
                tile = self.game.get_tile(self.ax + x, self.ay + y)
                if self.lives < 0 or self.game.detonated_count < self.lives:
                    tile = tile_hide.get(tile, tile)
                self.stdscr.addstr(
                    max_y - 2 - y,
                    x * 2,
                    " " + TILE_CHAR[tile],
                    get_color(*TILE_COLORS[tile]),
                )

    def print_status_bar(self) -> None:
        """
        Print status bar to screen.
        """
        max_y, max_x = self.stdscr.getmaxyx()
        x, y = self.cursor_location()

        lives_info = (
            "Inf" if self.lives < 0 else f"{self.lives - self.game.detonated_count}"
        )

        section_a = f" {self.game.density * 100:.1f}% "
        section_b = f" Lives: {lives_info:<4} Score: {len(self.game.uncovered)}"
        section_z = f"x: {x:<4} y: {y:<4} "

        self.stdscr.insstr(
            max_y - 1,
            0,
            section_b.ljust(max_x),
            get_color(curses.COLOR_CYAN, False) | curses.A_REVERSE,
        )
        self.stdscr.insstr(
            max_y - 1,
            0,
            section_a,
            get_color(curses.COLOR_MAGENTA, False) | curses.A_REVERSE,
        )
        if len(section_z) < max_x:
            self.stdscr.insstr(
                max_y - 1,
                max_x - len(section_z),
                section_z,
                get_color(curses.COLOR_CYAN, False) | curses.A_REVERSE,
            )

    def run(self) -> None:
        """
        Run the game.
        """
        init_colors()
        self.stdscr.clear()
        self.center_cursor()

        while True:
            max_y, _ = self.stdscr.getmaxyx()

            self.print_status_bar()
            self.print_grid()

            self.stdscr.move(max_y - 2 - self.cy, self.cx * 2 + 1)
            self.stdscr.refresh()
            curses.curs_set(2)

            match self.stdscr.get_wch():
                case "w":
                    self.scroll_by(0, 1)
                case "s":
                    self.scroll_by(0, -1)
                case "a":
                    self.scroll_by(-1, 0)
                case "d":
                    self.scroll_by(1, 0)
                case "W":
                    self.scroll_by(0, 5)
                case "S":
                    self.scroll_by(0, -5)
                case "A":
                    self.scroll_by(-5, 0)
                case "D":
                    self.scroll_by(5, 0)
                case curses.KEY_UP:
                    self.move_cursor(0, 1)
                case curses.KEY_DOWN:
                    self.move_cursor(0, -1)
                case curses.KEY_LEFT:
                    self.move_cursor(-1, 0)
                case curses.KEY_RIGHT:
                    self.move_cursor(1, 0)
                case "0":
                    self.scroll_to(0, 0)
                case "c":
                    self.center_cursor()
                case curses.KEY_ENTER | "\r" | "\n":
                    if self.game.uncover(*self.cursor_location()):
                        self.game.auto_chord(*self.cursor_location())
                case " ":
                    if not self.game.flag(*self.cursor_location()):
                        self.game.auto_chord(*self.cursor_location())
                case "r":
                    self.stdscr.clear()
                    self.stdscr.refresh()
                case "q":
                    if self.confirm_yn("Quit?"):
                        return
                    self.stdscr.erase()


def main(stdscr: curses.window, game: Minesweeper, lives: int) -> None:
    """
    Entry point for graphical minesweeper game. Call this function using
    `curses.wrapper`.
    """
    return TextUI(stdscr, game, lives).run()
