from __future__ import annotations

import curses

color_positions = {}


class Paint:
    window: "curses._CursesWindow"

    def load_colors(self):
        curses.start_color()
        curses.use_default_colors()

        try:
            for c in range(curses.COLORS):
                curses.init_pair(c + 1, c, -1)
        except (ValueError, curses.error):
            pass

    def show_palette(self):
        for color, posx in zip(
            range(self.color_range),
            range((self.maxx // 2) - (self.color_range * 2), self.maxx, 4),
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

        self.load_colors()
        window.nodelay(True)
        self.maxy, self.maxx = window.getmaxyx()

        self.window = window
        self.color_range = 256 // 32
        pressed = False
        current_color = -1

        self.show_palette()

        while True:
            key = self.window.getch()

            if key == curses.KEY_RESIZE:
                self.maxy, self.maxx = self.window.getmaxyx()
                self.window.clear()
                self.show_palette()

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
                    if current_color == -2:
                        self.window.addstr(y, x, "  ")
                    else:
                        self.window.addstr(y, x, "██", current_color)

            if key == ord("q"):
                self.window.clear()
                break

            if key == ord("c"):
                self.window.clear()
                self.show_palette()

            self.window.refresh()


curses.wrapper(Paint())
