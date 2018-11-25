import tkinter as tk

class MediaPlayerGUI(tk.Frame):
    def __init__(self, root, media_interface, *args, **kwargs):
        super(MediaPlayerGUI, self).__init__(root, *args, **kwargs)
        self.media_interface = media_interface

        tk.Label(self, text='Media Playback: ').pack(side=tk.LEFT)
        tk.Button(self, text='>', command=self.on_pause_btn_click).pack(side=tk.RIGHT)

    def on_pause_btn_click(self):
        if self.media_interface:
            self.media_interface.pause()

