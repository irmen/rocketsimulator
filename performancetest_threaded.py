"""
A rocket animation performance test
The rocket simulation and animations run in their own thread
the 'rendering' (drawing) in the main thread.

Copyright by Irmen de Jong (irmen@razorvine.net).
Open source software license: MIT.
"""
from __future__ import print_function, division
import random
import time
import threading
from vectors import Vector2D
from tkanimation import AnimationWindow, tkinter
from rocketsimulator import Rocket


class RocketSimulation(threading.Thread):
    def __init__(self, cwidth, cheight, start_num_rockets=10):
        super(RocketSimulation, self).__init__()
        self.cwidth = cwidth
        self.cheight = cheight
        self.rockets = []
        self.draw_calls = []
        self.framecounter = 0
        self.start_simulate = threading.Event()
        self.start_simulate.set()
        self.frame_done = threading.Event()
        self.add_rockets(start_num_rockets)
        self.start_time = time.time()
        self.daemon = True

    def add_rockets(self, count):
        for _ in range(count):
            self.add_rocket()

    def run(self):
        while True:
            self.start_simulate.wait()
            self.start_simulate.clear()
            for rocket in self.rockets:
                rocket.update()
                if not(-self.cwidth/2 < rocket.position.x < self.cwidth/2):
                    rocket.velocity.flipx()
                if not(0<rocket.position.y<self.cheight):
                    rocket.velocity.flipy()
            self.draw_calls = []
            for rocket in self.rockets:
                self.draw_calls.extend(rocket.draw_calls())
            self.framecounter += 1
            self.frame_done.set()

    def add_rocket(self):
        rocket = Rocket(self.cwidth, self.cheight)
        rocket.rotation_speed = random.uniform(-.3,.3)
        rocket.engine_throttle = 1
        rocket.position = Vector2D((random.randint(-self.cwidth/2,self.cwidth/2), random.randint(0,self.cheight)))
        rocket.velocity = Vector2D((random.uniform(-10,10), random.uniform(-4,4)))
        self.rockets.append(rocket)


class PerformanceTestWindow(AnimationWindow):
    def setup(self):
        self.cwidth, self.cheight = int(self.canvas["width"]), int(self.canvas["height"])
        self.simulation = RocketSimulation(self.cwidth, self.cheight, 10)
        self.simulation.start()
        self.set_frame_rate(60)

    def draw(self):
        # self.update()
        # wait for the simulation to complete the data for the new frame
        self.simulation.frame_done.wait()
        self.simulation.frame_done.clear()
        draw_calls = self.simulation.draw_calls
        self.simulation.start_simulate.set()
        # clear the screen and draw the next frame, while the simulation runs in the background thread for the next frame
        self.canvas.delete(tkinter.ALL)
        self.perform_draw_calls(draw_calls)
        # framecounter
        if time.time()-self.simulation.start_time:
            fps = int(self.simulation.framecounter / (time.time() - self.simulation.start_time))
        else:
            fps = 0
        self.canvas.create_text(self.cwidth, 0, text="#ROCKETS: {0:d}  FPS: {1:d} ".format(len(self.simulation.rockets), fps), fill="yellow", anchor=tkinter.NE)
        self.canvas.create_text(self.cwidth, 30, text="press SPACE to add 10 more ", fill="yellow", anchor=tkinter.NE)

    def perform_draw_calls(self, calls):
        for c in calls:
            getattr(self.canvas, c[0])(*c[1], **c[2])

    def keypress(self, char, mouseposition):
        if char==' ':
            self.simulation.add_rockets(10)
            self.simulation.framecounter = 0
            self.simulation.start_time = time.time()


if __name__ == "__main__":
    window = PerformanceTestWindow(1000, 600, "Rocket animation performance test")
    window.mainloop()
