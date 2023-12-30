from __future__ import annotations

import curses


color_positions = {}
movement_keys = {
    ord("w"): (-1, 0),
    ord("a"): (0, -1),
    ord("s"): (1, 0),
    ord("d"): (0, 1),
}


class Paint:
    window: "curses._CursesWindow"
    maxx: int
    maxy: int
    color_range: int
    grid: list[list[int]]
    cursor_x: int
    cursor_y: int

    def load_colors(self):
        curses.start_color()
        curses.use_default_colors()

        try:
            for c in range(curses.COLORS):
                curses.init_pair(c + 1, c, -1)
        except (ValueError, curses.error):
            pass

    def show_palette(self):
        color_range = 256 // 32

        for color, posx in zip(
            range(color_range),
            range((self.maxx // 2) - (color_range * 2), self.maxx, 4),
        ):
            pair = curses.color_pair(color + 1)
            color_positions[posx] = pair
            color_positions[posx + 1] = pair  # 1 color takes 2 positions
            self.window.addstr(self.maxy - 1, posx, "██", pair)

        for idx, letter in enumerate("ERASER"):
            self.window.addstr(self.maxy - 1, idx, letter)
            color_positions[idx] = -2  # i picked -2 for the color for eraser

    def __call__(self, window: "curses._CursesWindow"):
        curses.curs_set(0)
        curses.mousemask(curses.ALL_MOUSE_EVENTS)

        window.nodelay(True)

        self.use_cursor = False
        self.maxy, self.maxx = window.getmaxyx()
        self.cursor_x = self.maxx // 2
        self.cursor_y = self.maxy // 2

        # -2 are "empty" blocks
        self.grid = [[-2 for _ in range(self.maxx - 1)] for _ in range(self.maxy - 1)]
        self.load_colors()
        self.window = window

        current_color = -1
        pressed = False

        self.show_palette()

        while True:
            self.display()
            key = self.window.getch()

            if key == curses.KEY_RESIZE:
                new_maxy, new_maxx = self.window.getmaxyx()

                if new_maxy < self.maxy:
                    self.grid = self.grid[: new_maxy - 1]

                if new_maxx < self.maxx:
                    self.grid = [row[:new_maxx] for row in self.grid]

                if new_maxy > self.maxy:
                    self.grid += [
                        [-2 for _ in range(new_maxx)]
                        for _ in range(new_maxy - self.maxy)
                    ]

                if new_maxx > self.maxx:
                    for row in self.grid:
                        row += [-2 for _ in range(new_maxx - self.maxx)]

                self.maxy, self.maxx = new_maxy, new_maxx
                self.window.refresh()
                self.show_palette()

            if key in movement_keys and self.use_cursor:
                dy, dx = movement_keys[key]
                self.cursor_y += dy
                self.cursor_x += dx

                self.cursor_y %= self.maxy - 1
                self.cursor_x %= self.maxx - 1

            if key in (curses.KEY_ENTER, ord(" ")) and self.use_cursor:
                self.grid[self.cursor_y][self.cursor_x] = current_color

            if key == curses.KEY_MOUSE:
                _, x, y, _, bstate = curses.getmouse()

                if (
                    bstate & curses.BUTTON1_CLICKED
                    and y == self.maxy - 1
                    and x in color_positions
                ):
                    current_color = color_positions[x]

                if bstate & curses.BUTTON1_PRESSED:
                    pressed = True

                if bstate & curses.BUTTON1_RELEASED:
                    pressed = False

                if pressed and y < self.maxy - 1:
                    # 2 assignments so we paint 2 blocks lol
                    self.grid[y][x % (self.maxx - 1)] = current_color
                    self.grid[y][(x + 1) % (self.maxx - 1)] = current_color

            if key == ord("v"):
                self.use_cursor = not self.use_cursor

            if key == ord("q"):
                self.window.clear()
                break

            if key == ord("c"):
                self.window.clear()
                self.show_palette()

            self.window.refresh()

    def display(self):
        for y, row in enumerate(self.grid):
            for x, color in enumerate(row):
                if color == -2:
                    block, color = "  ", 0
                else:
                    block = "██"

                if self.cursor_y == y and self.cursor_x == x and self.use_cursor:
                    block = "+"

                try:
                    self.window.addstr(y, x, block, color)
                except curses.error:
                    # TODO: fix this
                    pass


curses.wrapper(Paint())
