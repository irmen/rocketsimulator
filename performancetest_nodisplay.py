"""
A rocket animation performance test (no display output).

Copyright by Irmen de Jong (irmen@razorvine.net).
Open source software license: MIT.
"""
from __future__ import print_function, division
import random
import time
import sys
from vectors import Vector2D
from rocketsimulator import Rocket

if sys.version_info < (3,0):
    input = raw_input


class DummyCanvas(object):
    def __getitem__(self, item):
        if item=="width":
            return 1000
        if item=="height":
            return 1000
        raise KeyError
    def create_polygon(self, points, outline="orange", fill="yellow"):
        pass


class PerformanceTest(object):
    def run(self):
        self.cwidth = 1000
        self.cheight = 1000
        self.rockets = []
        rockets_added_per_iteration = 200
        num_frames_per_iteration = 200
        while True:
            for _ in range(rockets_added_per_iteration):
                self.add_rocket()
            print("simulating {:d} frames with {:d} rockets...".format(num_frames_per_iteration, len(self.rockets)))
            start_time = time.time()
            self.simulate(num_frames_per_iteration)
            duration = time.time() - start_time
            print("   ... that took {:.2f} seconds; {:.2f} frames/sec".format(duration, num_frames_per_iteration/duration))
            input("\nenter to run again with {:d} extra rockets...:".format(rockets_added_per_iteration))

    def simulate(self, num_frames=10000):
        for _ in range(num_frames):
            self.update()
            for rocket in self.rockets:
                rocket.draw()

    def add_rocket(self):
        rocket = Rocket(DummyCanvas())
        rocket.rotation_speed = random.uniform(-.3,.3)
        rocket.engine_throttle = 1
        rocket.position = Vector2D((random.randint(-self.cwidth/2,self.cwidth/2), random.randint(0,self.cheight)))
        rocket.velocity = Vector2D((random.uniform(-10,10), random.uniform(-4,4)))
        self.rockets.append(rocket)

    def update(self):
        for rocket in self.rockets:
            rocket.update()
            if not(-self.cwidth/2 < rocket.position.x < self.cwidth/2):
                rocket.velocity.flipx()
            if not(0<rocket.position.y<self.cheight):
                rocket.velocity.flipy()


if __name__ == "__main__":
    test = PerformanceTest()
    test.run()
