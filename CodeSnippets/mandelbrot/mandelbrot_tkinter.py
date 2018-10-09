#!/usr/bin/python3

import sys
import time
import tkinter
from tkinter import messagebox

assert sys.version_info[0] > 2, "Python v3 is needed!"


class HumanDuration(object):
    CHUNKS = (
        (60 * 60 * 24 * 365, "years"),
        (60 * 60 * 24 * 30, "months"),
        (60 * 60 * 24 * 7, "weeks"),
        (60 * 60 * 24, "days"),
        (60 * 60, "hours"),
    )

    def __call__(self, t):
        if t < 1:
            return "%.1f ms" % round(t * 1000, 1)
        if t < 60:
            return "%.1f sec" % round(t, 1)
        if t < 60 * 60:
            return "%.1f min" % round(t / 60, 1)

        for seconds, name in self.CHUNKS:
            count = t / seconds
            if count >= 1:
                count = round(count, 1)
                break
        return "%.1f %s" % (count, name)


human_duration = HumanDuration()


def gen_pow(limit, reverse=True):

    interlace_steps = []
    step = 0
    while True:
        value = 2 ** step
        if value >= limit:
            break
        interlace_steps.append(value)
        step += 1

    if reverse:
        interlace_steps.reverse()
    return tuple(interlace_steps)


def interlace_generator(limit):

    interlace_steps = gen_pow(limit, reverse=True)

    # ~ print("interlace_steps:", interlace_steps)

    pos = 0
    step = 1
    iteration = 0
    size = interlace_steps[iteration]

    while True:
        yield pos, size
        pos += size * step

        if pos > limit:
            step = 2
            iteration += 1
            try:
                size = interlace_steps[iteration]
            except IndexError:
                return

            pos = size


class MultiStatusBar(tkinter.Frame):
    """ code from idlelib.MultiStatusBar.MultiStatusBar """

    def __init__(self, master, **kw):
        tkinter.Frame.__init__(self, master, **kw)
        self.labels = {}

    def set_label(self, name, text="", side=tkinter.LEFT):
        if name not in self.labels:
            label = tkinter.Label(self, bd=1, relief=tkinter.SUNKEN, anchor=tkinter.W)
            label.pack(side=side)
            self.labels[name] = label
        else:
            label = self.labels[name]
        label.config(text=text)


class MandelbrotTk(object):
    UPDATE_TIME = 0.2

    LEFT = -2
    RIGHT = 2
    TOP = 2
    BOTTOM = -2

    def __init__(self):
        self.iterations = 40
        self.width = self.height = 600

        self.root = tkinter.Tk()
        self.root.title("Mandelbrot in Tk by JensDiemer.de (GPL v3)")
        self.root.geometry("+%d+%d" % (self.root.winfo_screenwidth() * 0.1, self.root.winfo_screenheight() * 0.1))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.canvas = tkinter.Canvas(self.root, width=self.width, height=self.height, bd=0, bg="#000000")  # Border
        self.image = tkinter.PhotoImage(width=self.width, height=self.height)
        self.canvas.create_image(0, 0, image=self.image, state="normal", anchor=tkinter.NW)  # NW == NorthWest
        self.canvas.grid(row=0, column=0, sticky=tkinter.NSEW)

        self.status_bar = MultiStatusBar(self.root)
        if sys.platform == "darwin":
            # Insert some padding to avoid obscuring some of the statusbar
            # by the resize widget.
            self.status_bar.set_label("_padding1", "    ", side=tkinter.RIGHT)
        self.status_bar.grid(row=1, column=0)

        menubar = tkinter.Menu(self.root)

        filemenu = tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=filemenu)

        # help menu
        helpmenu = tkinter.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="help", command=self.menu_event_help)
        helpmenu.add_command(label="about", command=self.menu_event_about)
        menubar.add_cascade(label="help", menu=helpmenu)

        self.root.config(menu=menubar)

        self.root.bind("<Key>", self.event_key)
        self.root.update()

        self.render_after_id = None
        self.stats_after_id = None

    def menu_event_help(self):
        messagebox.showinfo("Help", "Zoom with: + / -\n" "Navigate with cursor keys!")

    def menu_event_about(self):
        messagebox.showinfo(
            "About", "Mandelbrot in Tkinter rendered with Python.\n" "By: Jens Diemer\n" "www.jensdiemer.de\n" "GPL v3"
        )

    def reset(self):
        self.horizontal_offset = 0
        self.vertical_offset = 0
        self.zoom = 1
        self.running = True

    def calc_dimensions(self):
        self.y = 0

        print("horizontal offset..:", self.horizontal_offset)
        print("vertical offset....:", self.vertical_offset)
        print("zoom...............:", self.zoom)
        self.left = (self.LEFT + self.horizontal_offset) * self.zoom
        self.right = (self.RIGHT + self.horizontal_offset) * self.zoom
        self.top = (self.TOP + self.vertical_offset) * self.zoom
        self.bottom = (self.BOTTOM + self.vertical_offset) * self.zoom
        print("Dimensions:", self.left, self.right, self.top, self.bottom)

        self.interlace_generator_next = interlace_generator(self.height).__next__  # Python 3
        self.done = False

    def event_key(self, event):
        keysym = event.keysym.lower()

        if keysym == "right":
            self.horizontal_offset -= 0.1
        elif keysym == "left":
            self.horizontal_offset += 0.1
        elif keysym == "up":
            self.vertical_offset -= 0.1
        elif keysym == "down":
            self.vertical_offset += 0.1
        elif keysym in ("plus", "kp_add"):
            self.zoom -= self.zoom * 0.1
            self.horizontal_offset += self.horizontal_offset * 0.1
            self.vertical_offset += self.vertical_offset * 0.1
        elif keysym in ("minus", "kp_subtract"):
            self.zoom += self.zoom * 0.1
        else:
            print("ignore keysym: %r" % keysym)
            return

        self.start_render_loop()

    def render_callback(self, x, y, count, size):
        # (r, g, b) = (count * 6, 0, 0)

        # red <-> green color ramp
        (r, g, b) = (
            (255 * count) // self.iterations,  # red
            (255 * (self.iterations - count)) // self.iterations,  # green
            0,  # blue
        )

        data = "#%02x%02x%02x" % (r, g, b)
        for offset in range(size):
            self.image.put(data, (x, y + offset))

        # Alternative:
        # But it's slower :(
        # self.canvas.create_line(x, y, x, y+size, fill=data)

    def _render_line(self, y, left, right, top, bottom, width, height, iterations, size, render_callback):
        data = ""
        for x in range(width):
            z = complex(0, 0)
            c = complex(left + x * (right - left) / width, top + y * (bottom - top) / height)
            norm = abs(z) ** 2
            for count in range(iterations):
                if norm <= 100:
                    z = z * z + c
                    norm = abs(z * z)
                else:
                    break

            render_callback(x, y, count, size)

    def status_callback(self, current_line):
        print("%.1f%%" % (float(current_line) / self.height * 100.0))
        self.root.update()

    def _render_loop(self):
        if not self.running or self.done:
            self._cancel_render_loop()
            self._cancel_stats_loop()
            return

        try:
            self.y, size = self.interlace_generator_next()
        except StopIteration:
            self.done = True
            duration = time.time() - self.start_time
            msg = "%ix%ipx Rendered in %iSec." % (self.width, self.height, duration)
            self.status_bar.set_label("process", msg)
            self._cancel_render_loop()
            return

        # FIXME: work-a-round for slowiness in render_callback()
        if size > 16:
            size = 16

        self._render_line(
            self.y,
            self.left,
            self.right,
            self.top,
            self.bottom,
            self.width,
            self.height,
            self.iterations,
            size,
            render_callback=self.render_callback,
        )
        self.root.update_idletasks()
        self.render_after_id = self.root.after_idle(func=self._render_loop)

    def _cancel_render_loop(self):
        print("_cancel_render_loop()")
        if self.render_after_id is not None:
            self.root.after_cancel(self.render_after_id)
            self.render_after_id = None
        self.running = False

    def init_display_stats(self):
        print("init_display_stats()")
        self.last_pos = 0
        self.start_time = self.last_update = time.time()

    def _cancel_stats_loop(self):
        print("_cancel_stats_loop()")
        if self.stats_after_id is not None:
            self.root.after_cancel(self.stats_after_id)
            self.stats_after_id = None

    def _display_stats_loop(self):
        pos = self.y * self.width
        pos_diff = pos - self.last_pos
        self.last_pos = pos

        duration = time.time() - self.last_update
        self.last_update = time.time()

        rate = pos_diff / duration
        percent = 100.0 * self.y / self.height
        self.status_bar.set_label("process", "%.1f%% (%i Pixel/sec.)" % (percent, rate))
        self.stats_after_id = self.root.after(ms=500, func=self._display_stats_loop)

    def start_render_loop(self):
        self._cancel_render_loop()
        self._cancel_stats_loop()

        self.calc_dimensions()
        self.init_display_stats()

        self.running = True
        self._display_stats_loop()
        self._render_loop()

    def mainloop(self):
        self.reset()
        self.start_render_loop()
        self.root.mainloop()


if __name__ == "__main__":
    mandelbrot_tk = MandelbrotTk()
    mandelbrot_tk.mainloop()
