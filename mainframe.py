import tkinter as tk
import json

import intervaltimer.adapters
from tkinter import messagebox

from intervaltimer.intervaltimer import IntervalTimer
from intervaltimer.adapters import schedule_to_interval_timer_script
from mediaplayer.vlcconnection import VLCConnection
from mediaplayer.vlcmusicmanager import VLCMusicManager
from practiceschedule.scheduleeditor import ScheduleEditor
from practiceschedule.scheduleeditorcontroller import ScheduleEditorController
from soundmanager.announcementtimehandler import AnnouncementTimeHandler
from soundmanager.soundmanager import SoundManager


class App(tk.Tk):
    def __init__(self, announcement_handler = None, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self.announcement_handler = announcement_handler

        # Load up preferences
        self.load_prefs()

        # Gui Setup
        # Menu setup
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff = 0)
        filemenu.add_command(label='Exit', command=self.on_close)
        menubar.add_cascade(label='File', menu=filemenu)

        viewmenu = tk.Menu(menubar, tearoff = 0)
        self.viewmenu_option = tk.IntVar()
        viewmenu.add_radiobutton(label='Schedule', value=1, variable=self.viewmenu_option, command=self.change_view)
        viewmenu.add_radiobutton(label='Interval Timer', value=2, variable=self.viewmenu_option, command=self.change_view)
        self.viewmenu_option.set(1)
        menubar.add_cascade(label='View', menu=viewmenu)
        self.config(menu=menubar)

        # Frame set ups
        self.mainframe = tk.Frame(self)
        self.mainframe.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.mainframe.grid_rowconfigure(0, weight=1)
        self.mainframe.grid_columnconfigure(0, weight=1)

        self.frames = {}

        self.schedule_editor_controller = ScheduleEditorController()
        self.frames[ScheduleEditor] = ScheduleEditor(self.mainframe, self.schedule_editor_controller)
        self.frames[ScheduleEditor].grid(row = 0, column = 0, sticky='NSEW')

        self.frames[IntervalTimer] = None

        self.current_frame = self.frames[ScheduleEditor]
        self.current_frame.tkraise()

    def load_prefs(self):
        try:
            with open('prefs.json', 'r') as file:
                prefs_dict = json.load(file)
        except (IOError, json.decoder.JSONDecodeError) as e:
            messagebox.showerror('Load Preferences Error', str(e))
        # Convert the json dictionary to a more appropriate dictionary for the program
        self.prefs_dict = {}
        # Handle interval timer prefs
        try:
            self.prefs_dict['interval_timer_prefs'] = prefs_dict['interval_timer_prefs']
        except KeyError:
            messagebox.showerror('Load Preferences Error', 'Couldn\'t load interval timer preferences.')
            self.prefs_dict['interval_timer_prefs'] = None
        # Handle announcement time prefs
        try:
            announcement_time_prefs_string_keys = prefs_dict['announcement_time_prefs']
            self.prefs_dict['announcement_time_prefs'] = intervaltimer.adapters.convert_to_interval_timer_period_announcement_times(
                announcement_time_prefs_string_keys)
        except KeyError:
            messagebox.showerror('Load Preferences Error', 'Couldn\'t load announcement time preferences')
            self.prefs_dict['announcement_time_prefs'] = intervaltimer.adapters.get_default_interval_timer_period_announcement_times()

    def change_view(self):
        if self.viewmenu_option.get() == 1:
            if self.frames[IntervalTimer]:
                # Clear interval timer out
                self.prefs_dict['interval_timer_prefs'] = self.frames[IntervalTimer].get_prefs_as_dict()
                self.frames[IntervalTimer].grid_forget()
                self.frames[IntervalTimer].destroy()
                self.frames[IntervalTimer] = None
            self.current_frame = self.frames[ScheduleEditor]
        elif self.viewmenu_option.get() == 2:
            if len(self.schedule_editor_controller.schedule.periods) >= 1:
                # Set up interval timer script
                interval_timer_script = schedule_to_interval_timer_script(self.schedule_editor_controller.schedule,
                                                                          self.prefs_dict['announcement_time_prefs'])
                self.frames[IntervalTimer] = IntervalTimer(self.mainframe, interval_timer_script,
                                                           self.prefs_dict['interval_timer_prefs'])
                self.frames[IntervalTimer].grid(row=0, column=0, sticky='NSEW')
                self.frames[IntervalTimer].announcement_callback = self.announcement_handler
                self.current_frame = self.frames[IntervalTimer]
            else:
                messagebox.showerror('Interval Timer Error', 'Script must have at least one period.')
                self.viewmenu_option.set(1)

        self.current_frame.tkraise()

    def setup_interval_timer(self):
        interval_timer_script = schedule_to_interval_timer_script(self.schedule_editor_controller.schedule, self.prefs_dict['announcement_time_prefs'])
        self.frames[IntervalTimer] = IntervalTimer(self.mainframe, interval_timer_script, self.prefs_dict['interval_timer_prefs'])
        self.frames[IntervalTimer].grid(row=0, column=0, sticky='NSEW')
        self.frames[IntervalTimer].announcement_callback = self.announcement_handler

    def save_prefs(self):
        try:
            if self.frames[IntervalTimer]:
                self.prefs_dict['interval_timer_prefs'] = self.frames[IntervalTimer].get_prefs_as_dict()
            with open('prefs.json', 'w') as file:
                json.dump(self.prefs_dict, file, indent=4)
        except IOError as e:
            messagebox.showerror('Save Preferences Error', 'Couldn\'t save preferences')

    def on_close(self):
        self.save_prefs()
        self.destroy()

if __name__=='__main__':
    #attempt to load up vlc and wire the announcement handler
    try:
        vlc_connection = VLCConnection(r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe")
        vlc_music_manager = VLCMusicManager(vlc_connection)
        vlc_connection.vlc_message_callback = vlc_music_manager.receive_vlc_messages
        vlc_loaded = True
    except FileNotFoundError:
        vlc_loaded = False
        vlc_connection = None
        vlc_music_manager = None
    sound_manager = SoundManager('sounds', vlc_music_manager)
    announcement_handler = AnnouncementTimeHandler(sound_manager)

    root = App()
    root.announcement_handler = announcement_handler.handle_script_announcements

    if not vlc_loaded:
        messagebox.showerror('Connect to VLC Error', 'Couldn\'t connect to VLC')

    def on_close():
        if vlc_connection:
            vlc_connection.vlc_subprocess.kill()
        root.on_close()
    root.state('zoomed')
    root.protocol('WM_DELETE_WINDOW', on_close)
    root.mainloop()
