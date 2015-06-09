#!/usr/bin/python
# coding: UTF-8

from __future__ import absolute_import, division, print_function
import colorsys
import random

import sys
import time

try:
    import pyglet
except ImportError as err:
    print("Error: 'pyglet' not installed? (%s)" % err)
    print("\nPlease install pyglet:")
    print("https://pyglet.readthedocs.org/en/latest/programming_guide/installation.html")
    sys.exit(-1)


class HumanDuration(object):
    CHUNKS = (
        (60 * 60 * 24 * 365, 'years'),
        (60 * 60 * 24 * 30, 'months'),
        (60 * 60 * 24 * 7, 'weeks'),
        (60 * 60 * 24, 'days'),
        (60 * 60, 'hours'),
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


def interlace_generator(limit):
    def gen_pow(limit):
        interlace_steps = []
        step = 0
        while True:
            value = 2 ** step
            if value >= limit:
                return interlace_steps
            interlace_steps.append(value)
            step += 1

    interlace_steps = gen_pow(limit)
    interlace_steps.reverse()
    # ~ print("interlace_steps:", interlace_steps)

    index = 0
    pos = 0
    step = 1
    iteration = 0
    size = interlace_steps[iteration]

    while True:
        index += 1
        yield (index, pos, size, iteration)
        pos += (size * step)

        if pos > limit:
            step = 2
            iteration += 1
            try:
                size = interlace_steps[iteration]
            except IndexError:
                return

            pos = size


class Mandelbrot(object):
    LEFT = -2.0
    RIGHT = 2.0
    TOP = 2.0
    BOTTOM = -2.0

    def __init__(self, draw_callback, width, height):
        self.draw_callback = draw_callback
        self.width = width
        self.height = height

        self.iterations = 40
        self.resolution = 4

        self.color_functions = []
        for attr_name in dir(self):
            if attr_name.startswith("color_func_"):
                self.color_functions.append(
                    getattr(self, attr_name)
                )

        self.color_func = self.color_functions[0]

        self.center()

    def center(self):
        print("center()")
        self.horizontal_offset = 0
        self.vertical_offset = 0
        self.zoom = 1.0
        self.calc_dimensions()
        self.reset()

    def reset(self):
        print("reset()")
        self.change_scale = 0.5
        self.index = 1
        self.y = 0
        self.step = self.height // 4
        self.line_count = 0
        self.last_update = self.start_time = time.time()
        self.last_pos = 0
        self.done = False
        self.running = True
        _interlace_generator = interlace_generator(self.height)
        try:
            self.interlace_generator_next = _interlace_generator.next # Python 2
        except AttributeError:
            self.interlace_generator_next = _interlace_generator.__next__ # Python 3

    def calc_dimensions(self):
        print("calc_dimensions()")
        print("offset [h,v].......: %s, %s" % (
            self.horizontal_offset, self.vertical_offset
        ))
        print("zoom...............: x%.1f (%s)" % (1 / self.zoom, self.zoom))

        self.left = (self.LEFT * self.zoom) + self.horizontal_offset
        self.right = (self.RIGHT * self.zoom) + self.horizontal_offset
        self.top = (self.TOP * self.zoom) + self.vertical_offset
        self.bottom = (self.BOTTOM * self.zoom) + self.vertical_offset
        print("coordinates........:", self.left, self.right, self.top, self.bottom)

        # self.iterations = int(1 / self.zoom)*10
        print("Iterations.........:", self.iterations)

        self.reset()

    def increase_iterations(self):
        new_iterations = int(self.iterations * 1.1)
        if new_iterations == self.iterations:
            self.iterations += 1
        else:
            self.iterations = new_iterations
        self.reset()

    def decrease_iterations(self):
        self.iterations = max([int(self.iterations * 0.9), 1])
        self.reset()
        
    def increase_resolution(self):
        new_resolution = int(self.resolution * 1.1)
        if new_resolution == self.resolution:
            self.resolution += 1
        else:
            self.resolution = new_resolution
        self.reset()

    def decrease_resolution(self):
        self.resolution = max([int(self.resolution * 0.9), 1])
        self.reset()

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.reset()

    def move_right(self):
        self.horizontal_offset += (self.change_scale * self.zoom)
        self.calc_dimensions()

    def move_left(self):
        self.horizontal_offset -= (self.change_scale * self.zoom)
        self.calc_dimensions()

    def move_top(self):
        self.vertical_offset += (self.change_scale * self.zoom)
        self.calc_dimensions()

    def move_bottom(self):
        self.vertical_offset -= (self.change_scale * self.zoom)
        self.calc_dimensions()

    def zoom_in(self):
        self.zoom -= self.zoom * self.change_scale
        self.horizontal_offset -= self.horizontal_offset * self.zoom
        self.vertical_offset -= self.vertical_offset * self.zoom
        self.calc_dimensions()

    def zoom_out(self):
        self.zoom += self.zoom * self.change_scale
        self.horizontal_offset -= self.horizontal_offset * self.zoom
        self.vertical_offset -= self.vertical_offset * self.zoom
        self.calc_dimensions()

    #-------------------------------------------------------------------
    # color functions
    #-------------------------------------------------------------------

    def color_func_monochrome_red(self, count, norm, iterations):
        return (int(256 / iterations * norm), 0, 0)

    RANDOM_MAP={}
    def color_func_random(self, count, norm, iterations):
        try:
            return self.RANDOM_MAP[count]
        except KeyError:
            self.RANDOM_MAP[count] = (r,g,b) = (random.randrange(255),random.randrange(255),random.randrange(255))
            return (r,g,b)

    def color_func_hsv2rgb(self, count, norm, iterations):
        # very colorfull ;)
        (r,g,b) = colorsys.hsv_to_rgb(h=norm/iterations,s=1,v=1)
        return int(r*255), int(g*255), int(b*255)

    def color_func_red_green_ramp(self, count, norm, iterations):
        # red <-> green color ramp
        return (
            (255 * count) // iterations, # red
            (255 * (iterations - count)) // iterations, # green
            0, # blue
        )

    def color_func_red_green_ramp_hard(self, count, norm, iterations):
        return (
            int((255 * norm) / iterations), # red
            int((255 * (iterations - norm)) // iterations), # green
            0, # blue
        )

    def color_func_color_steps(self, count, norm, iterations):
        if count <= 5:
            return (0, (255 // 5) * count, 0) # monochrome green
        elif count <= 8:
            return (0, 255, 0) # green
        elif count <= 10:
            return (0, 0, 255) # blue
        elif count <= 12:
            return (255, 0, 0) # red
        elif count <= 15:
            return (255, 255, 0) # yellow
        else:
            return (0, 0, 0) # black

    def color_func_psychedelic(self, count, norm, iterations):
        # Psychedelic colors:
        color = int((65536.0 / iterations) * count)
        return (
            (color >> 16) & 0xFF, # red
            (color >> 8) & 0xFF, # green
            color & 0xFF, # blue
        )

    COLOR_MAP = {
        0: (66, 30, 15),
        1: (25, 7, 26),
        2: (9, 1, 47),
        3: (4, 4, 73),
        4: (0, 7, 100),
        5: (12, 44, 138),
        6: (24, 82, 177),
        7: (57, 125, 209),
        8: (134, 181, 229),
        9: (211, 236, 248),
        10: (241, 233, 191),
        11: (248, 201, 95),
        12: (255, 170, 0),
        13: (204, 128, 0),
        14: (153, 87, 0),
        15: (106, 52, 3),
        16: (90, 40, 0),
        17: (40, 20, 0),
        18: (20, 10, 0),
        19: (10, 5, 0),
        20: (5, 0, 0),
    }
    def color_func_color_map(self, count, norm, iterations):
        try:
            return self.COLOR_MAP[count]
        except KeyError:
            if count <= 33:
                return (count * 7, count * 5, 0)
            else:
                return (0, 0, 0) # black

    #-------------------------------------------------------------------
    # color functions
    #-------------------------------------------------------------------

    def get_color_func_name(self):
        return self.color_func.__name__

    def next_color_func(self):
        try:
            self.color_func = self.color_functions[self.color_functions.index(self.color_func)+1]
        except IndexError:
            self.color_func = self.color_functions[0]
        self.reset()

    def previous_color_func(self):
        try:
            self.color_func = self.color_functions[self.color_functions.index(self.color_func)-1]
        except IndexError:
            self.color_func = self.color_functions[-1]
        self.reset()

    def _render_line(self, draw_callback, color_func, y, left, right, top, bottom, width, height, iterations, size):
        count = None

        # resolution = int(1 / self.zoom)+1
        resolution = self.resolution

        x_factor = right - left
        y_factor = bottom - top
        aspect_ratio = float(width) / height

        for x in range(width):
            x2 = x * aspect_ratio
            z = complex(0, 0)
            c = complex(left + (x2 * x_factor / width), top + (y * y_factor / height))
            norm = abs(z) ** 2
            for count in range(iterations):
                if norm <= resolution:
                    z = z ** 2 + c
                    norm = abs(z ** 2)
                else:
                    break

            (r, g, b) = color_func(count, norm, iterations)
            draw_callback(x, y, r, g, b, size)

    def render_line(self):
        try:
            (self.index, self.y, size, iteration) = self.interlace_generator_next()
        except StopIteration:
            self.done = True
            self.running = False
            duration = time.time() - self.start_time
            msg = "%ix%ipx Rendered in %iSec." % (self.width, self.height, duration)
            print(msg)
            return

        # print("render line:", self.y)

        self._render_line(
            self.draw_callback,
            self.color_func,
            self.y,
            self.left, self.right, self.top, self.bottom,
            self.width, self.height, self.iterations,
            size,
        )

    def get_percent(self):
        return 100.0 * self.index / self.height


class InfoWindowPyglet(pyglet.window.Window):
    def __init__(self, parent):
        self.parent = parent
        super(InfoWindowPyglet, self).__init__(
            width=parent.width, height=200,
            style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS,
            resizable=False
        )
        self.move_to_parent()

    def move_to_parent(self):
        self.width = self.parent.width
        x,y=self.parent.get_location()
        self.set_location(x,y+self.parent.height)

    def on_draw(self):
        self.clear()

        mandelbrot = self.parent.mandelbrot

        msg = (
            "Zoom with mouse wheel.\n"
            "Move by drag the mouse.\n"
            "Use right mouse click to center\n"
        )
        msg += "%i%%\n" % mandelbrot.get_percent()
        msg += "zoom: x%.1f\n" % (1 / mandelbrot.zoom)
        msg += "iterations: %i (change with 'i' and 'o')\n" % mandelbrot.iterations
        msg += "resolution: %i (change with 'r' and 't')\n" % mandelbrot.resolution
        msg += "coordinates: %f, %f, %f, %f\n" % (
            mandelbrot.left, mandelbrot.right,
            mandelbrot.top, mandelbrot.bottom
        )
        msg += "Color func: %s (change with 'c' and 'v')\n" % mandelbrot.get_color_func_name()
        label = pyglet.text.Label(msg,
            x=20, y=self.height-20,
            font_size=10,
            width=self.parent.width-20,
            multiline=True,
        )
        label.draw()



class MandelbrotPyglet(pyglet.window.Window):
    def __init__(self, width=800, height=800):
        super(MandelbrotPyglet, self).__init__(width, height, resizable=True)

        self.set_caption("Mandelbrot in pyglet by JensDiemer.de (GPL v3)")
        self.set_location(100, 100)

        self.mandelbrot = Mandelbrot(draw_callback=self.draw_pixel, width=self.width, height=self.height)

        self.info_window = InfoWindowPyglet(self)

        self.reset()

    def reset(self):
        self.pixel_batch = pyglet.graphics.Batch()
        self.line_batch = pyglet.graphics.Batch()

    def draw_pixel(self, x, y, r, g, b, size):
        """
        draw one line/pixel

        FIXME: Why is there a x offset between GL_LINES and GL_POINTS ?!?
        """
        if size > 1:
            self.line_batch.add(
                2, # The number of vertices in the list.
                pyglet.gl.GL_LINES, # OpenGL drawing mode
                None, # Group of the vertex list, or None if no group is required.
                ('v2i', (x, y, x, y+size)),
                ('c3B', (r, g, b, r, g, b)),
            )
        else:
            self.pixel_batch.add(
                1, # The number of vertices in the list.
                pyglet.gl.GL_POINTS, # OpenGL drawing mode
                None, # Group of the vertex list, or None if no group is required.
                ('v2i', (x-1, y)),
                ('c3B', (r, g, b)) # data items
            )

    def on_resize(self, width, height):
        print("on_resize()", width, height)
        super(MandelbrotPyglet, self).on_resize(width, height)

        if width != self.mandelbrot.width or height != self.mandelbrot.height:
            print("do resize!")
            self.mandelbrot.resize(width, height)
            self.info_window.move_to_parent()

    def on_move(self, x, y):
        self.info_window.move_to_parent()

    def on_draw(self):
        self.clear()
        self.line_batch.draw()
        self.pixel_batch.draw()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        direction = scroll_y
        print("on_mouse_scroll:", x, y, scroll_x, scroll_y)
        if direction > 0:
            self.mandelbrot.zoom_in()
        else:
            self.mandelbrot.zoom_out()
        self.reset()

    def on_mouse_press(self, x, y, button, modifiers):
        if button & pyglet.window.mouse.RIGHT:
            self.mandelbrot.center()
            self.mandelbrot.calc_dimensions()
            self.reset()

    def on_key_press(self, symbol, modifiers):
    # def on_key_release(self, symbol, modifiers):
        print("on_key_release():", symbol, modifiers)

        if symbol==pyglet.window.key.I:
            self.mandelbrot.increase_iterations()
        elif symbol==pyglet.window.key.O:
            self.mandelbrot.decrease_iterations()

        elif symbol==pyglet.window.key.R:
            self.mandelbrot.increase_resolution()
        elif symbol==pyglet.window.key.T:
            self.mandelbrot.decrease_resolution()

        elif symbol==pyglet.window.key.C:
            self.mandelbrot.next_color_func()
        elif symbol==pyglet.window.key.V:
            self.mandelbrot.previous_color_func()

        self.reset()

    drag_scale = 0.05
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        # print("on_mouse_drag:", x, y, dx, dy, buttons, modifiers)
        # print("on_mouse_drag:", dx, dy)

        self.mandelbrot.horizontal_offset += (-dx * self.drag_scale * self.mandelbrot.zoom)
        self.mandelbrot.vertical_offset += (dy * self.drag_scale * self.mandelbrot.zoom)
        self.mandelbrot.calc_dimensions()
        self.reset()

    def main_loop(self):
        next_update = time.time() + 0.25
        while not self.has_exit:
            pyglet.clock.tick()

            for window in pyglet.app.windows:
                window.switch_to()
                window.dispatch_events()
                window.dispatch_event('on_draw')
                window.flip()

            while not self.mandelbrot.done and time.time() < next_update:
                self.mandelbrot.render_line()
            next_update = time.time() + 0.25


if __name__ == "__main__":
    width = height = 600
    mandelbrot = MandelbrotPyglet(width, height)
    mandelbrot.main_loop()

    print(" --- END --- ")
