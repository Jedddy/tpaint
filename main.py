from __future__ import annotations

import curses

color_positions = {}

class Paint:
    window: "curses._CursesWindow"

    def __call__(self, window: "curses._CursesWindow"):
        curses.curs_set(0)
        curses.mousemask(curses.ALL_MOUSE_EVENTS)
        curses.start_color()
        curses.use_default_colors()

        # window.nodelay(True)
        maxy, maxx = window.getmaxyx()

        try:
            for c in range(curses.COLORS):
                curses.init_pair(c + 1, c, -1)
        except (ValueError, curses.error):
            pass

        self.window = window
        color_range = 256 // 32
        pressed = False
        current_color = - 1

        while True:
            for color, posx in zip(
                range(color_range),
                range((maxx // 2) - (color_range  * 2), maxx, 4)
            ):
                pair = curses.color_pair(color + 1)
                color_positions[posx] = pair
                color_positions[posx + 1] = pair  # 1 color takes 2 positions
                self.window.addstr(maxy - 1, posx, "██", pair)

            key = self.window.getch()

            if key == curses.KEY_RESIZE:
                maxy, maxx = self.window.getmaxyx()
                self.window.clear()

            if key == curses.KEY_MOUSE:
                _, x, y, _, bstate = curses.getmouse()

                if (
                    bstate & curses.BUTTON1_CLICKED and
                    y == maxy - 1 and
                    x in color_positions
                ):
                    current_color = color_positions[x]

                if bstate & curses.BUTTON1_PRESSED:
                    pressed = True

                if bstate & curses.BUTTON1_RELEASED:
                    pressed = False

                if pressed and y < maxy - 1:
                    self.window.addstr(y, x, "██", current_color)

            elif key == ord("q"):
                break

            self.window.refresh()


curses.wrapper(Paint())
