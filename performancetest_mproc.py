"""
A rocket animation performance test
The rocket simulation and animations run in their own thread
the 'rendering' (drawing) in the main thread.

Copyright by Irmen de Jong (irmen@razorvine.net).
Open source software license: MIT.
"""
from __future__ import print_function, division
import Pyro4
import time
from tkanimation import AnimationWindow, tkinter


Pyro4.config.SERIALIZER = "marshal"


class PerformanceTestWindow(AnimationWindow):
    def setup(self):
        self.cwidth, self.cheight = int(self.canvas["width"]), int(self.canvas["height"])
        self.simulation = Pyro4.Proxy("PYRO:rocket_simulation@localhost:33444")
        self.framerate = 200
        self.start_time = time.time()
        self.framecounter = 0
        self.num_rockets = 10
        self.simulation.init(self.cwidth, self.cheight, self.num_rockets)

    def draw(self):
        # self.update()
        draw_calls = self.simulation.get_next_frame()
        self.framecounter += 1
        self.canvas.delete(tkinter.ALL)
        self.perform_draw_calls(draw_calls)
        # framecounter
        if time.time()-self.start_time:
            fps = int(self.framecounter / (time.time() - self.start_time))
        else:
            fps = 0
        self.canvas.create_text(self.cwidth, 0, text="#ROCKETS: {0:d}  FPS: {1:d} ".format(self.num_rockets, fps), fill="yellow", anchor=tkinter.NE)
        self.canvas.create_text(self.cwidth, 30, text="press SPACE to add 10 more ", fill="yellow", anchor=tkinter.NE)

    def perform_draw_calls(self, calls):
        for c in calls:
            getattr(self.canvas, c[0])(*c[1], **c[2])

    def keypress(self, char, mouseposition):
        if char==' ':
            self.num_rockets += 10
            self.simulation.add_rockets(10)
            self.framecounter = 0
            self.start_time = time.time()


if __name__ == "__main__":
    window = PerformanceTestWindow(1000, 600, "Rocket animation performance test")
    window.mainloop()
