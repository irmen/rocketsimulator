"""
A rocket animation performance test
This is the simulation server part. Start this in a separate process.

Copyright by Irmen de Jong (irmen@razorvine.net).
Open source software license: MIT.
"""
from __future__ import print_function, division
import random
import Pyro4
from vectors import Vector2D
from rocketsimulator import Rocket


class RocketSimulation:
    @Pyro4.expose
    def init(self, cwidth, cheight, start_num_rockets=10):
        self.cwidth = cwidth
        self.cheight = cheight
        self.rockets = []
        self.add_rockets(start_num_rockets)

    @Pyro4.expose
    def add_rockets(self, count):
        for _ in range(count):
            self.add_rocket()

    @Pyro4.expose
    def get_next_frame(self):
        for rocket in self.rockets:
            rocket.update()
            if not(-self.cwidth/2 < rocket.position.x < self.cwidth/2):
                rocket.velocity.flipx()
            if not(0<rocket.position.y<self.cheight):
                rocket.velocity.flipy()
        draw_calls = []
        for rocket in self.rockets:
            draw_calls.extend(rocket.draw_calls())
        return draw_calls

    def add_rocket(self):
        rocket = Rocket(self.cwidth, self.cheight)
        rocket.rotation_speed = random.uniform(-.3,.3)
        rocket.engine_throttle = 1
        rocket.position = Vector2D((random.randint(-self.cwidth/2,self.cwidth/2), random.randint(0,self.cheight)))
        rocket.velocity = Vector2D((random.uniform(-10,10), random.uniform(-4,4)))
        self.rockets.append(rocket)


Pyro4.config.SERVERTYPE = "multiplex"
Pyro4.config.SERIALIZERS_ACCEPTED = {"marshal"}   # fastest for simple types
Pyro4.Daemon.serveSimple({
        RocketSimulation: "rocket_simulation"
    }, port=33444, ns=False)
