# coding: utf-8

import time
import Tkinter as tkinter

WIDTH = 640
HEIGHT = 480
LEFT = -2
RIGHT = 0.5
TOP = 1.25
BOTTOM = -1.25
ITERATIONS = 40
UPDATE_TIME = 0.75


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


root = tkinter.Tk()
image = tkinter.PhotoImage(width=WIDTH, height=HEIGHT)
lb1 = tkinter.Label(root, image=image)
lb1.pack()


start_time = time.time()
time_threshold = start_time + (UPDATE_TIME / 2)


pixel_count = 0
total_count = HEIGHT * WIDTH
for y in range(HEIGHT):
    for x in range(WIDTH):
        z = complex(0, 0)
        c = complex(LEFT + x * (RIGHT - LEFT) / WIDTH, TOP + y * (BOTTOM - TOP) / HEIGHT)
        norm = abs(z) ** 2
        for count in xrange(ITERATIONS):
            if norm <= 4.0:
                z = z * z + c
                norm = abs(z * z)
            else:
                break

        if count <= 4:
            (r, g, b) = (128, 128, 128) # grey
        elif count <= 8:
            (r, g, b) = (0, 255, 0) # green
        elif count <= 10:
            (r, g, b) = (0, 0, 255) # blue
        elif count <= 12:
            (r, g, b) = (255, 0, 0) # red
        elif count <= 15:
            (r, g, b) = (255, 255, 0) # yellow
        else:
            (r, g, b) = (0, 0, 0) # black

        (r, g, b) = (count * 6, 0, 0)

        pixel_count += 1
        image.put("#%02x%02x%02x" % (r, g, b), (x, y))

        current_time = time.time()
        if current_time > (time_threshold + UPDATE_TIME):

            elapsed = float(current_time - start_time)      # Vergangene Zeit
            estimated = elapsed / pixel_count * total_count # Geschätzte Zeit
            remain = estimated - elapsed
            performance = pixel_count / elapsed
            percent = round(float(pixel_count) / total_count * 100.0, 2)

            print (
                "   "
                "%(percent).1f%%"
                " - current: %(elapsed)s"
                " - total: %(estimated)s"
                " - remain: %(remain)s"
                " - %(perf).1f pixel/sec"
                "   "
            ) % {
                "percent"  : percent,
                "elapsed"  : human_duration(elapsed),
                "estimated": human_duration(estimated),
                "remain"   : human_duration(remain),
                "perf"     : performance,
            }

            time_threshold = current_time

            root.update()

root.mainloop()
