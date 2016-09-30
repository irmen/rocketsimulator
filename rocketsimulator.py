"""
A rocket simulation dexterity game!

Copyright by Irmen de Jong (irmen@razorvine.net).
Open source software license: MIT.
"""
from __future__ import print_function, division
import time
from vectors import Vector2D

try:
    from tkinter import *
except ImportError:
    from Tkinter import *


class AnimationWindow(Tk):
    """
    Base class for tkinter animation windows. Creates window and binds keyboard events to react upon.
    """
    def __init__(self, width, height, windowtitle="animation engine"):
        Tk.__init__(self)
        self.wm_title(windowtitle)
        self.bind("<KeyPress>", lambda event: self.keypress(event.char, (event.x, event.y)))
        self.bind("<KeyRelease>", lambda event: self.keyrelease(event.char, (event.x, event.y)))
        self.canvas = Canvas(self, width=width, height=height, background="black", borderwidth=0, highlightthickness=0)
        self.canvas.pack()
        self.framerate = 30
        self.continue_animation = True
        self.setup()
        self.after(100, self.__process_frame)

    def __process_frame(self):
        start = time.time()
        self.draw()
        if self.continue_animation:
            duration = time.time() - start
            budget = 1/self.framerate
            self.after(int(1000*(budget-duration))-2, self.__process_frame)

    def stop(self):
        self.continue_animation = False

    def setup(self):
        pass

    def draw(self):
        pass

    def keypress(self, char, mouseposition):
        pass

    def keyrelease(self, char, mouseposition):
        pass


class Rocket(object):
    """
    Rocket with one main engine at the tail, and two RCS thrusters on the left and right side.
    The main engine provides force to move the rocket forwards, the RCS (reaction control system)
    thrusters provide rotation around the rocket's center of mass (somewhere in the lower section)
    """
    def __init__(self, canvas, initial_x_position=None):
        self.canvas = canvas
        self.cwidth, self.cheight = int(canvas["width"]), int(canvas["height"])
        self.rocket_vertices = [(-2, 0), (-1, 1), (-1, 7), (0, 8), (1, 7), (1, 1), (2, 0)]
        self.rotation_point = (0, 2.5)
        self.engine_flame_vertices = [(-1, 0), (-1.5, -2), (-0.5, -2), (-1, -4), (0, -3), (1, -4), (0.5, -2), (1.5, -2), (1, 0)]
        self.thruster_positions = [(-1.5, 7), (1.5, 7)]
        self.set_touchdown_position(initial_x_position or 0.0)

    def set_touchdown_position(self, x_position):
        self.position = Vector2D((x_position, 0))
        self.velocity = Vector2D((0, 0))
        self.acceleration = Vector2D((0, 0))
        self.rotation = 0.0
        self.rotation_speed = 0.0
        self.rotation_acceleration = 0.0
        self.crashed = False
        self.touchdown = True
        self.engine_throttle = 0.0
        self.right_thruster_on = False
        self.left_thruster_on = False

    def update(self):
        self.velocity += self.acceleration
        self.position += self.velocity
        self.acceleration *= 0
        self.rotation += self.rotation_speed
        self.rotation_speed += self.rotation_acceleration
        self.rotation_acceleration = 0.0
        if self.position.y <= 0:
            if 0 < self.velocity.length < 2 and abs(self.rotation) < 0.1:
                # safe touchdown (low velocity and almost no rotation)
                print("touchdown!", self.position, self.rotation)
                self.set_touchdown_position(self.position.x)
            elif self.velocity.length > 0:
                print("crash on ground", self.position, self.rotation)
                self.crashed = True
        self.touchdown = self.position.y==0 and self.velocity.length==0
        if self.position.x <= self.cwidth/-2 or self.position.x >= self.cwidth/2 or self.position.y >= self.cheight:
            print("crashed out of range", self.position)
            self.crashed = True

    def apply_force(self, force):
        self.acceleration += force

    def apply_rotation(self, force):
        self.rotation_acceleration += force

    def draw(self):
        screen_offset = Vector2D((self.cwidth/2, 10))
        screen_offset += self.position
        scale = 6
        # rotate and position the rocket
        points = (Vector2D(xy) for xy in self.rocket_vertices)
        if self.velocity.length:
            points = (v.rotate_around(self.rotation_point, self.rotation) for v in points)
        points = (scale*v+screen_offset for v in points)
        points = [(v.x, self.cheight-v.y) for v in points]
        self.canvas.create_polygon(points, fill="blue", outline="lightgrey")
        if self.engine_throttle:
            # rotate and position the engine flame
            points = ((x, y*self.engine_throttle) for x, y in self.engine_flame_vertices)
            points = (Vector2D(xy) for xy in points)
            if self.velocity.length:
                points = (v.rotate_around(self.rotation_point, self.rotation) for v in points)
            points = (scale*v+screen_offset for v in points)
            points = [(v.x, self.cheight-v.y) for v in points]
            self.canvas.create_polygon(points, outline="orange", fill="yellow")
        # rotate and position the left and right thrusters
        points = (Vector2D(xy) for xy in self.thruster_positions)
        if self.velocity.length:
            points = (v.rotate_around(self.rotation_point, self.rotation) for v in points)
        points = (scale*v+screen_offset for v in points)
        points = [(v.x, self.cheight-v.y) for v in points]
        if self.left_thruster_on:
            self.canvas.create_oval(points[0][0]-3, points[0][1]-3, points[0][0]+3, points[0][1]+3, outline="orange", fill="yellow")
        if self.right_thruster_on:
            self.canvas.create_oval(points[1][0]-3, points[1][1]-3, points[1][0]+3, points[1][1]+3, outline="orange", fill="yellow")

    def apply_gravity(self, gravity):
        # if the rocket is flying (and not standing on a launch pad), gravity has effect
        if self.position.y > 0 or self.velocity.length > 0:
            self.apply_force(Vector2D((0, -gravity)))  # gravity is a force pointing downwards


class Launchpad(object):
    """
    Rocket launchpad where a rocket can safely land and takeoff from.
    """
    width = 50

    def __init__(self, canvas, x):
        self.canvas = canvas
        self.cwidth, self.cheight = int(canvas["width"]), int(canvas["height"])
        self.x = x - self.width/2

    def draw(self):
        self.canvas.create_rectangle(self.x, self.cheight-11, self.x+self.width, self.cheight-5, outline="gray80", fill="gray60")

    def is_rocket_above(self, rocket):
        rocket_screen_x = self.cwidth/2 + rocket.position.x
        return self.x < rocket_screen_x < self.x+self.width


class RocketSimulatorWindow(AnimationWindow):
    """
    The actual rocket landing simulatino game window!
    """
    def setup(self):
        self.cwidth, self.cheight = int(self.canvas["width"]), int(self.canvas["height"])
        self.framerate = 30
        self.launchpad_offset = self.cwidth/6
        initial_x_pos = self.launchpad_offset-self.cwidth/2
        self.rocket = Rocket(self.canvas, initial_x_pos)
        self.launchpad_start = Launchpad(self.canvas, self.launchpad_offset)
        self.launchpad_destination = Launchpad(self.canvas, self.cwidth-self.launchpad_offset)
        self.framecounter = 0

    def draw(self):
        self.update()
        self.canvas.delete(ALL)
        # ground:
        self.canvas.create_rectangle(0, self.cheight-10, self.cwidth-1, self.cheight-1, outline="chocolate", fill="sienna")
        # launch pads:
        self.launchpad_start.draw()
        self.launchpad_destination.draw()
        # instructions and telemetry:
        instructions = """*** Launch the rocket and land it successfully at the other launchpad ***

space bar to fire main engine normally
v   to fire main engine (2x throttle)
[   right RCS thruster
]   left RCS thruster"""
        self.canvas.create_text(220, self.cheight/2-220, text=instructions, fill="green", anchor=W)
        self.canvas.create_text(220, self.cheight/2-140, text="rocket position = ({0:.2f}, {1:.2f})"
                                .format(self.rocket.position.x, self.rocket.position.y), fill="green", anchor=W)
        self.canvas.create_text(220, self.cheight/2-120, text="velocity = {0:.2f}   (vx: {1:.2f} vy: {2:.2f})"
                                .format(self.rocket.velocity.length, self.rocket.velocity.x, self.rocket.velocity.y), fill="green", anchor=W)
        self.canvas.create_text(220, self.cheight/2-100, text="rotation speed = {0:.2f}"
                                .format(self.rocket.rotation_speed), fill="green", anchor=W)
        # finally the rocket
        self.rocket.draw()
        if self.rocket.crashed:
            self.canvas.create_text(self.cwidth/2, self.cheight/2, text="ROCKET LOST !!!", fill="pink")
            self.stop()
        if self.rocket.touchdown:
            location = "SOMEWHERE..."
            if self.launchpad_start.is_rocket_above(self.rocket):
                location = "ON LAUNCHPAD ALPHA - READY FOR TAKEOFF"
            if self.launchpad_destination.is_rocket_above(self.rocket):
                location = "ON LAUNCHPAD BETA - WELL DONE!"
            self.canvas.create_text(self.cwidth/2, self.cheight/2, text="ROCKET TOUCHDOWN\n"+location, fill="pink")

    def update(self):
        self.framecounter += 1
        if self.rocket.engine_throttle:
            engine_force = Vector2D((0, .2 * self.rocket.engine_throttle)).rotate(self.rocket.rotation)    # accelerate along rocket's orientation
            self.rocket.apply_force(engine_force)
        if self.rocket.right_thruster_on:
            self.rocket.apply_rotation(0.005)
        if self.rocket.left_thruster_on:
            self.rocket.apply_rotation(-0.005)
        self.rocket.apply_gravity(0.1)
        self.rocket.update()

    def keypress(self, char, mouseposition):
        if char == ' ':
            self.rocket.engine_throttle = 1.0    # regular 100% thrust
        elif char == 'v':
            self.rocket.engine_throttle = 2.0    # 200% thrust
        elif char == '[':
            self.rocket.right_thruster_on = True
        elif char == ']':
            self.rocket.left_thruster_on = True

    def keyrelease(self, char, mouseposition):
        if char in (' ', 'v'):
            self.rocket.engine_throttle = 0.0
        elif char == '[':
            self.rocket.right_thruster_on = False
        elif char == ']':
            self.rocket.left_thruster_on = False


if __name__ == "__main__":
    window = RocketSimulatorWindow(1000, 600, "Rocket launch and landing simulator")
    window.mainloop()
