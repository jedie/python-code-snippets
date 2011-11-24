#!/usr/bin/env python
# encoding: utf-8

"""
    This file contains definitions for a simple raytracer.
   
    modified 2011 by Jens Diemer:
        Display the picture live in a Tkinter window

    Origin sourcecode from:
        http://www.lshift.net/~tonyg/raytrace.py
    see also:
        http://www.lshift.net/blog/2008/10/29/toy-raytracer-in-python
    Copyright Callum and Tony Garnock-Jones, 2008.

    This file may be freely redistributed under the MIT license,
    http://www.opensource.org/licenses/mit-license.php
"""

from __future__ import with_statement
import time

try:
    import psyco
    from psyco.classes import *
    psyco.log()
    psyco.profile(0.05)
    psyco.full()
    print 'Using psyco.'
except ImportError:
    print 'Not using psyco.'

import math
import Tkinter as tkinter

EPSILON = 0.00001


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


class PointVectorBase(object):
    def __init__(self, initx, inity, initz):
        self.x = initx
        self.y = inity
        self.z = initz

    def __str__(self):
        return '(%s,%s,%s)' % (self.x, self.y, self.z)

    def __repr__(self):
        if self.isPoint():
            kind = "Point"
        else:
            kind = "Vector"
        return '%s(%s,%s,%s)' % (kind, self.x, self.y, self.z)


class Vector(PointVectorBase):
    def magnitude(self):
        return math.sqrt(self.dot(self))

    def __add__(self, other):
        if other.isPoint():
            return Point(self.x + other.x, self.y + other.y, self.z + other.z)
        else:
            return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        other.mustBeVector()
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def scale(self, factor):
        return Vector(factor * self.x, factor * self.y, factor * self.z)

    def dot(self, other):
        other.mustBeVector()
        return (self.x * other.x) + (self.y * other.y) + (self.z * other.z)

    def cross(self, other):
        other.mustBeVector()
        return Vector(self.y * other.z - self.z * other.y,
                      self.z * other.x - self.x * other.z,
                      self.x * other.y - self.y * other.x)

    def normalized(self):
        return self.scale(1.0 / self.magnitude())

    def negated(self):
        return self.scale(-1)

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y) and (self.z == other.z)

    def isVector(self):
        return True

    def isPoint(self):
        return False

    def mustBeVector(self):
        return self

    def mustBePoint(self):
        raise 'Vectors are not points!'

    def reflectThrough(self, normal):
        d = normal.scale(self.dot(normal))
        return self -d.scale(2)


Vector.ZERO = Vector(0, 0, 0)
Vector.RIGHT = Vector(1, 0, 0)
Vector.UP = Vector(0, 1, 0)
Vector.OUT = Vector(0, 0, 1)

assert Vector.RIGHT.reflectThrough(Vector.UP) == Vector.RIGHT
assert Vector(-1, -1, 0).reflectThrough(Vector.UP) == Vector(-1, 1, 0)


class Point(PointVectorBase):
    def __add__(self, other):
        other.mustBeVector()
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        if other.isPoint():
            return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
        else:
            return Point(self.x - other.x, self.y - other.y, self.z - other.z)

    def isVector(self):
        return False

    def isPoint(self):
        return True

    def mustBeVector(self):
        raise 'Points are not vectors!'

    def mustBePoint(self):
        return self


class Sphere(object):
    def __init__(self, centre, radius):
        centre.mustBePoint()
        self.centre = centre
        self.radius = radius

    def __repr__(self):
        return 'Sphere(%s,%s)' % (repr(self.centre), self.radius)

    def intersectionTime(self, ray):
        cp = self.centre - ray.point
        v = cp.dot(ray.vector)
        discriminant = (self.radius * self.radius) - (cp.dot(cp) - v * v)
        if discriminant < 0:
            return None
        else:
            return v - math.sqrt(discriminant)

    def normalAt(self, p):
        return (p - self.centre).normalized()


class Halfspace(object):
    def __init__(self, point, normal):
        self.point = point
        self.normal = normal.normalized()

    def __repr__(self):
        return 'Halfspace(%s,%s)' % (repr(self.point), repr(self.normal))

    def intersectionTime(self, ray):
        v = ray.vector.dot(self.normal)
        if v:
            return 1 / -v
        else:
            return None

    def normalAt(self, p):
        return self.normal


class Ray(object):
    def __init__(self, point, vector):
        self.point = point
        self.vector = vector.normalized()
#        self.vector.jitter()

    def __repr__(self):
        return 'Ray(%s,%s)' % (repr(self.point), repr(self.vector))

    def pointAtTime(self, t):
        return self.point + self.vector.scale(t)


Point.ZERO = Point(0, 0, 0)

a = Vector(3, 4, 12)
b = Vector(1, 1, 1)


class PpmCanvas(object):
    def __init__(self, width, height, filenameBase):
        import array
        self.bytes = array.array('B', [0] * (width * height * 3))
        for i in range(width * height):
            self.bytes[i * 3 + 2] = 255
        self.width = width
        self.height = height
        self.filenameBase = filenameBase

    def plot(self, x, y, r, g, b):
        i = ((self.height - y - 1) * self.width + x) * 3
        self.bytes[i  ] = max(0, min(255, int(r * 255)))
        self.bytes[i + 1] = max(0, min(255, int(g * 255)))
        self.bytes[i + 2] = max(0, min(255, int(b * 255)))

    def update(self):
        pass

    def save(self):
        with open(self.filenameBase + '.ppm', 'wb') as f:
            f.write('P6 %d %d 255\n' % (self.width, self.height))
            f.write(self.bytes.tostring())


class TkCanvas(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.root = tkinter.Tk()
        self.image = tkinter.PhotoImage(width=self.width, height=self.height)
        lb1 = tkinter.Label(self.root, image=self.image)
        lb1.pack()

        self.root.update()

    def plot(self, x, y, r, g, b):
        r = max(0, min(255, int(r * 255)))
        g = max(0, min(255, int(g * 255)))
        b = max(0, min(255, int(b * 255)))

        y = self.height - y

        self.image.put("#%02x%02x%02x" % (r, g, b), (x, y))

    def update(self):
        self.root.update()

    def save(self):
        pass


def firstIntersection(intersections):
    result = None
    for i in intersections:
        candidateT = i[1]
        if candidateT is not None and candidateT > -EPSILON:
            if result is None or candidateT < result[1]:
                result = i
    return result


def addColours(a, scale, b):
    return (a[0] + scale * b[0],
            a[1] + scale * b[1],
            a[2] + scale * b[2])


class SimpleSurface(object):
    def __init__(self, **kwargs):
        self.baseColour = kwargs.get('baseColour', (1, 1, 1))
        self.specularCoefficient = kwargs.get('specularCoefficient', 0.2)
        self.lambertCoefficient = kwargs.get('lambertCoefficient', 0.6)
        self.ambientCoefficient = 1.0 - self.specularCoefficient - self.lambertCoefficient

    def baseColourAt(self, p):
        return self.baseColour

    def colourAt(self, scene, ray, p, normal):
        b = self.baseColourAt(p)

        c = (0, 0, 0)
        if self.specularCoefficient > 0:
            reflectedRay = Ray(p, ray.vector.reflectThrough(normal))
            #print p, normal, ray.vector, reflectedRay.vector
            reflectedColour = scene.rayColour(reflectedRay)
            c = addColours(c, self.specularCoefficient, reflectedColour)

        if self.lambertCoefficient > 0:
            lambertAmount = 0
            for lightPoint in scene.visibleLights(p):
                contribution = (lightPoint - p).normalized().dot(normal)
                if contribution > 0:
                    lambertAmount = lambertAmount + contribution
            lambertAmount = min(1, lambertAmount)
            c = addColours(c, self.lambertCoefficient * lambertAmount, b)

        if self.ambientCoefficient > 0:
            c = addColours(c, self.ambientCoefficient, b)

        return c


class CheckerboardSurface(SimpleSurface):
    def __init__(self, **kwargs):
        SimpleSurface.__init__(self, **kwargs)
        self.otherColour = kwargs.get('otherColour', (0, 0, 0))
        self.checkSize = kwargs.get('checkSize', 1)

    def baseColourAt(self, p):
        v = p - Point.ZERO
        v.scale(1.0 / self.checkSize)
        if (int(abs(v.x) + 0.5) + \
            int(abs(v.y) + 0.5) + \
            int(abs(v.z) + 0.5)) \
           % 2:
            return self.otherColour
        else:
            return self.baseColour


class Scene(object):
    def __init__(self, canvas, update_time=0.5, max_recursion_depth=3):
        self.canvas = canvas
        self.update_time = update_time
        self.max_recursion_depth = max_recursion_depth
        self.objects = []
        self.lightPoints = []
        self.position = Point(0, 1.8, 10)
        self.lookingAt = Point.ZERO
        self.fieldOfView = 45
        self.recursionDepth = 0

    def moveTo(self, p):
        self.position = p

    def lookAt(self, p):
        self.lookingAt = p

    def addObject(self, obj, surface):
        self.objects.append((obj, surface))

    def addLight(self, p):
        self.lightPoints.append(p)

    def render(self):
        print 'Computing field of view'
        fovRadians = math.pi * (self.fieldOfView / 2.0) / 180.0
        halfWidth = math.tan(fovRadians)
        halfHeight = 0.75 * halfWidth
        width = halfWidth * 2
        height = halfHeight * 2
        pixelWidth = width / (self.canvas.width - 1)
        pixelHeight = height / (self.canvas.height - 1)

        eye = Ray(self.position, self.lookingAt - self.position)
        vpRight = eye.vector.cross(Vector.UP).normalized()
        vpUp = vpRight.cross(eye.vector).normalized()

        start_time = time.time()
        next_update = start_time + self.update_time

        print 'Looping over pixels'
        for y in xrange(self.canvas.height):

            if time.time() > next_update:
                self.canvas.update()
                current_time = time.time()
                next_update = current_time + self.update_time
                self.print_status(start_time, current_time, y)

            for x in xrange(self.canvas.width):
                xcomp = vpRight.scale(x * pixelWidth - halfWidth)
                ycomp = vpUp.scale(y * pixelHeight - halfHeight)
                ray = Ray(eye.point, eye.vector + xcomp + ycomp)
                colour = self.rayColour(ray)
                self.canvas.plot(x, y, *colour)

        self.print_status(start_time, time.time(), self.canvas.height)
        self.canvas.save()
        print 'Complete.'

    def print_status(self, start_time, current_time, y):
        percent = round(float(y) / self.canvas.height * 100, 2)

        elapsed = current_time - start_time      # Vergangene Zeit
        estimated = elapsed / y * self.canvas.height # Geschätzte Zeit

        remain = estimated - elapsed

        performance = y * self.canvas.width / elapsed

        print (
            "   "
            "%(percent).1f%%"
            " - elapsed: %(elapsed)s"
            " - estimated: %(estimated)s"
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

    def rayColour(self, ray):
        if self.recursionDepth > self.max_recursion_depth:
            return (0, 0, 0)
        try:
            self.recursionDepth = self.recursionDepth + 1
            intersections = [(o, o.intersectionTime(ray), s) for (o, s) in self.objects]
            i = firstIntersection(intersections)
            if i is None:
                return (0, 0, 0) ## the background colour
            else:
                (o, t, s) = i
                p = ray.pointAtTime(t)
                return s.colourAt(self, ray, p, o.normalAt(p))
        finally:
            self.recursionDepth = self.recursionDepth - 1

    def _lightIsVisible(self, l, p):
        for (o, s) in self.objects:
            t = o.intersectionTime(Ray(p, l - p))
            if t is not None and t > EPSILON:
                return False
        return True

    def visibleLights(self, p):
        result = []
        for l in self.lightPoints:
            if self._lightIsVisible(l, p):
                result.append(l)
        return result


if __name__ == '__main__':
    #Canvas = PpmCanvas
    Canvas = TkCanvas

    canvas = Canvas(320, 240)
    #canvas = Canvas(640, 480, 'test_raytrace_big')

    s = Scene(canvas, update_time=1, max_recursion_depth=2)

    s.addLight(Point(30, 30, 10))
    s.addLight(Point(-10, 100, 30))
    s.lookAt(Point(0, 3, 0))
    s.addObject(Sphere(Point(1, 3, -10), 2), SimpleSurface(baseColour=(1, 1, 0)))
    for y in range(6):
        s.addObject(Sphere(Point(-3 - y * 0.4, 2.3, -5), 0.4),
                    SimpleSurface(baseColour=(y / 6.0, 1 - y / 6.0, 0.5)))
    s.addObject(Halfspace(Point(0, 0, 0), Vector.UP), CheckerboardSurface())

    start_time = time.time()
    s.render()
    print "Rendered in %.1fsec" % (time.time() - start_time)

    canvas.root.mainloop()
