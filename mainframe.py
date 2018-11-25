import tkinter as tk
import json
import intervaltimer.adapters
from tkinter import messagebox

from intervaltimer.intervaltimer import IntervalTimer
from intervaltimer.adapters import schedule_to_interval_timer_script
from mediaplayer.vlcconnection import VLCConnection
from mediaplayer.vlcmusicmanager import VLCMusicManager
from misc.intervaltimerexception import IntervalTimerException
from practiceschedule.scheduleeditor import ScheduleEditor
from practiceschedule.scheduleeditorcontroller import ScheduleEditorController
from prefs import save_prefs, load_prefs
from soundmanager.announcementtimehandler import AnnouncementTimeHandler
from soundmanager.soundmanager import SoundManager


class App(tk.Tk):
    def __init__(self, prefs, announcement_handler, media_interface, external_interface, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        #initialize passed in values
        self.announcement_handler = announcement_handler
        self.prefs_dict = prefs
        self.media_interface = media_interface
        self.external_interface = None

        # Gui Setup
        # Menu setup
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff = 0)
        file_menu.add_command(label='Exit', command=self.on_close)
        menu_bar.add_cascade(label='File', menu=file_menu)

        view_menu = tk.Menu(menu_bar, tearoff = 0)
        self.view_menu_option = tk.IntVar()
        view_menu.add_radiobutton(label='Schedule', value=1, variable=self.view_menu_option, command=self.change_view)
        view_menu.add_radiobutton(label='Interval Timer', value=2, variable=self.view_menu_option, command=self.change_view)
        self.view_menu_option.set(1)
        menu_bar.add_cascade(label='View', menu=view_menu)
        self.config(menu=menu_bar)

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


    def change_view(self):
        if self.view_menu_option.get() == 1:
            if self.frames[IntervalTimer]:
                # Clear interval timer out
                self.prefs_dict['interval_timer_prefs'] = self.frames[IntervalTimer].get_prefs_as_dict()
                self.frames[IntervalTimer].grid_forget()
                self.frames[IntervalTimer].destroy()
                self.frames[IntervalTimer] = None
            self.current_frame = self.frames[ScheduleEditor]
            if self.external_interface:
                self.external_interface.interval_timer = None
        elif self.view_menu_option.get() == 2:
            if len(self.schedule_editor_controller.schedule.periods) >= 1:
                # Set up interval timer script
                interval_timer_script = schedule_to_interval_timer_script(self.schedule_editor_controller.schedule,
                                                                          self.prefs_dict['announcement_time_prefs'])
                self.frames[IntervalTimer] = IntervalTimer(self.mainframe, interval_timer_script, self.media_interface,
                                                           self.prefs_dict['interval_timer_prefs'])
                self.frames[IntervalTimer].grid(row=0, column=0, sticky='NSEW')
                self.frames[IntervalTimer].announcement_callback = self.announcement_handler
                self.current_frame = self.frames[IntervalTimer]
                if self.external_interface:
                    self.external_interface.interval_timer = self.frames[IntervalTimer]
            else:
                messagebox.showerror('Interval Timer Error', 'Script must have at least one period.')
                self.view_menu_option.set(1)

        self.current_frame.tkraise()


    def on_close(self):
        if self.frames[IntervalTimer]:
            self.prefs_dict['interval_timer_prefs'] = self.frames[IntervalTimer].get_prefs_as_dict()
        try:
            save_prefs(self.prefs_dict)
        except IntervalTimerException:
            messagebox.showerror('Save Preferences Error', 'Couldn\'t save preferences')

        self.destroy()


if __name__=='__main__':
    prefs, load_pref_errors = load_prefs()

    #attempt to load up vlc and wire the announcement handler
    try:
        vlc_connection = VLCConnection(prefs['vlc_prefs']['vlc_path'])
        vlc_music_manager = VLCMusicManager(vlc_connection)
        vlc_connection.vlc_message_callback = vlc_music_manager.receive_vlc_messages
        vlc_loaded = True
    except FileNotFoundError:
        vlc_loaded = False
        vlc_connection = None
        vlc_music_manager = None
    sound_manager = SoundManager('sounds', vlc_music_manager)
    announcement_handler = AnnouncementTimeHandler(sound_manager)

    root = App(prefs, announcement_handler.handle_script_announcements, vlc_music_manager, None)

    if load_pref_errors:
        messagebox.showerror('Load preference errors', load_pref_errors)
    if not vlc_loaded:
        messagebox.showerror('Connect to VLC Error', 'Couldn\'t connect to VLC')

    def on_close():
        if vlc_connection:
            vlc_connection.vlc_subprocess.kill()
        root.on_close()

    root.state('zoomed')
    root.protocol('WM_DELETE_WINDOW', on_close)
    root.mainloop()
