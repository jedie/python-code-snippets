#!/usr/bin/python
# coding: UTF-8

from __future__ import absolute_import, division, print_function

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
        step=0
        while True:
            value = 2**step
            if value>=limit:
                return interlace_steps
            interlace_steps.append(value)
            step+=1
    interlace_steps = gen_pow(limit)
    interlace_steps.reverse()
    #~ print("interlace_steps:", interlace_steps)

    index = 0
    pos = 0
    step = 1
    iteration = 0
    size = interlace_steps[iteration]

    while True:
        index += 1
        yield (index, pos, size, iteration)
        pos += (size * step)

        if pos>limit:
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

        self.running = True

        self.center()
        self.reset()
        self.calc_dimensions()

    def center(self):
        print("center")
        self.horizontal_offset = 0
        self.vertical_offset = 0
        self.zoom = 1.0
        self.reset()

    def reset(self):
        print("reset")
        self.iterations=40
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
        print("offset [h,v].......: %s, %s" % (
            self.horizontal_offset, self.vertical_offset
        ))
        print("zoom...............: x%.1f (%s)" % (1/self.zoom, self.zoom))

        self.left=(self.LEFT * self.zoom) + self.horizontal_offset
        self.right=(self.RIGHT * self.zoom) + self.horizontal_offset
        self.top=(self.TOP * self.zoom) + self.vertical_offset
        self.bottom=(self.BOTTOM * self.zoom) + self.vertical_offset
        print("coordinates........:", self.left, self.right, self.top, self.bottom)

        # print("Iterations.........:", self.iterations)

        self.color_func = self.color_func_red_green_ramp # red <-> green color ramp

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

    def color_func_red_green_ramp(self, count, norm, iterations):
        # red <-> green color ramp
        return (
            (255 * count) // iterations, # red
            (255 * (iterations - count)) // iterations, # green
            0, # blue
        )

    def _render_line(self, draw_callback, color_func, y, left, right, top, bottom, width, height, iterations, size):
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

            (r,g,b)=color_func(count, norm, iterations)
            draw_callback(x, y, r, g, b, size)

    def render_line(self):
        # if not self.running or self.done:
        #     self._cancel_render_loop()
        #     return

        try:
            (self.index, self.y, size, iteration) = self.interlace_generator_next()
        except StopIteration:
            self.done = True
            self.running = False
            duration = time.time() - self.start_time
            msg = "%ix%ipx Rendered in %iSec." % (self.width, self.height, duration)
            print(msg)
            return

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



class MandelbrotPyglet(pyglet.window.Window):
    def __init__(self, width=800, height=800):
        super(MandelbrotPyglet, self).__init__(width, height)

        self.set_caption("Mandelbrot in Tk by JensDiemer.de (GPL v3)")
        self.set_location(100,100)

        self.mandelbrot = Mandelbrot(draw_callback=self.draw_pixel, width=self.width, height=self.height)
        self.reset()

    def reset(self):
        self.pixel_batch = pyglet.graphics.Batch()
        self.line_batch = pyglet.graphics.Batch()

    def draw_pixel(self, x, y, r, g, b, size):
        if size>1:
            self.line_batch.add(
                2, # The number of vertices in the list.
                pyglet.gl.GL_LINES, # OpenGL drawing mode
                None, # Group of the vertex list, or None if no group is required.
                ('v2i', (x,y, x,y+size)),
                ('c3B', (r,g,b, r,g,b)),
            )
        else:
            self.pixel_batch.add(
                1, # The number of vertices in the list.
                pyglet.gl.GL_POINTS, # OpenGL drawing mode
                None, # Group of the vertex list, or None if no group is required.
                ('v2i', (x,y)),
                ('c3B', (r,g,b)) # data items
            )

    def on_draw(self):
        self.clear()
        self.line_batch.draw()
        self.pixel_batch.draw()

        msg = "%i%%" % self.mandelbrot.get_percent()
        label = pyglet.text.Label(msg,x=18,y=18)
        label.draw()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        direction = scroll_y
        print("on_mouse_scroll:", x, y, scroll_x, scroll_y)
        if direction>0:
            self.mandelbrot.zoom_in()
        else:
            self.mandelbrot.zoom_out()
        self.reset()

    def on_mouse_press(self, x, y, button, modifiers):
        if button & pyglet.window.mouse.RIGHT:
            self.mandelbrot.center()
            self.mandelbrot.calc_dimensions()
            self.reset()

    drag_scale=0.05
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

            self.switch_to()
            self.dispatch_events()
            self.dispatch_event('on_draw')
            self.flip()

            while not self.mandelbrot.done and time.time()<next_update:
                self.mandelbrot.render_line()
            next_update = time.time() + 0.25


if __name__ == "__main__":
    width=height=600
    mandelbrot = MandelbrotPyglet(width, height)
    mandelbrot.main_loop()

    print(" --- END --- ")