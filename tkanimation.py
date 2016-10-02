"""
TkInter animation stuff.

Copyright by Irmen de Jong (irmen@razorvine.net).
Open source software license: MIT.
"""
from __future__ import print_function, division
import time

try:
    import tkinter
except ImportError:
    import Tkinter as tkinter


class AnimationWindow(tkinter.Tk):
    """
    Base class for tkinter animation windows. Creates window and binds keyboard events to react upon.
    """
    def __init__(self, width, height, windowtitle="animation engine"):
        tkinter.Tk.__init__(self)
        self.wm_title(windowtitle)
        self.bind("<KeyPress>", lambda event: self.keypress(*self._keyevent(event)))
        self.bind("<KeyRelease>", lambda event: self.keyrelease(*self._keyevent(event)))
        self.canvas = tkinter.Canvas(self, width=width, height=height, background="black", borderwidth=0, highlightthickness=0)
        self.canvas.pack()
        self.framerate = 30
        self.continue_animation = True
        self.setup()
        self.after(100, self.__process_frame)

    def __process_frame(self):
        start = time.time()
        if self.continue_animation:
            self.draw()
        duration = time.time() - start
        budget = 1/self.framerate
        sleep = int(1000*(budget-duration))-2
        if sleep < 1:
            self.after_idle(self.__process_frame)
        else:
            self.after(sleep, self.__process_frame)

    def _keyevent(self, event):
        c = event.char
        if not c or ord(c)>255:
            c = event.keysym
        return c, (event.x, event.y)

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

