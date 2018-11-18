import tkinter as tk

class IntervalTimer(tk.Frame):
    def __init__(self, root):
        super(IntervalTimer, self).__init__(root)
        self.script = None