import tkinter as tk

class MediaPlayerGUI(tk.Frame):
    def __init__(self, *args, **kwargs):
        super(MediaPlayerGUI, self).__init__(*args, **kwargs)

        tk.Label(self, text='Media Playback: ').pack(side=tk.LEFT)
        tk.Button(self, text='>', command=self.on_pause_btn_click).pack(side=tk.RIGHT)

    def on_pause_btn_click(self):
        if hasattr(self, 'on_pause'):
            self.on_pause()

