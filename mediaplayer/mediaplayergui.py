import tkinter as tk

class MediaPlayerGUI(tk.Frame):
    def __init__(self,*args, **kwargs):
        tk_frame_kwargs = {key:item for key, item in kwargs.items() if key not in ['on_pause']}
        super(MediaPlayerGUI, self).__init__(*args, **tk_frame_kwargs)
        self.__dict__.update({key:item for key, item in kwargs.items() if key in ['on_pause']})

        tk.Label(self, text='Media Playback: ').pack(side=tk.LEFT)
        tk.Button(self, text='>', command=self.on_pause_btn_click).pack(side=tk.RIGHT)

    def on_pause_btn_click(self):
        if hasattr(self, 'on_pause'):
            self.on_pause()

