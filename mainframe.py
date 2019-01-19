import os
import tkinter as tk
import sys
import threading
import mediaplayer.musiclibrary as ml
from tkinter import messagebox
from tkinter import filedialog

from intervaltimer.intervaltimer import IntervalTimer
from intervaltimer.adapters import schedule_to_interval_timer_script
from intervaltimer.tcpinterface import TCPInterface
from mediaplayer.automaticvlcmusicmanager import AutomaticVLCMusicManager
from mediaplayer.vlcconnection import VLCConnection
from mediaplayer.vlcmusicmanager import VLCMusicManager
from misc.intervaltimerexception import IntervalTimerException
from practiceschedule.scheduleeditor import ScheduleEditor
from prefs import save_prefs, load_prefs
from soundmanager.announcementtimehandler import AnnouncementTimeHandler
from soundmanager.soundmanager import SoundManager


class App(tk.Tk):
    def __init__(self, prefs, announcement_handler, media_interface, remote_address, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        #initialize passed in values
        self.announcement_handler = announcement_handler
        self.prefs_dict = prefs
        self.media_interface = media_interface
        self.last_schedule_directory = self.prefs_dict['schedule_prefs']['last_schedule_directory']
        self.modify_interval_timer_lock = threading.Lock()

        # Gui Setup
        # Menu setup
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff = 0)
        file_menu.add_command(label='Load Schedule', command=self.on_load_schedule)
        file_menu.add_command(label='Save Schedule', command=self.on_save_schedule)
        file_menu.add_separator()
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
        tk.Label(text=remote_address).pack()

        self.frames = {}

        self.frames[ScheduleEditor] = ScheduleEditor(self.mainframe)
        self.frames[ScheduleEditor].grid(row = 0, column = 0, sticky='NSEW')

        self.frames[IntervalTimer] = None

        self.current_frame = self.frames[ScheduleEditor]
        self.current_frame.tkraise()

    def on_load_schedule(self):
        try:
            if self.last_schedule_directory:
                initial_dir = self.last_schedule_directory
            else:
                initial_dir = os.getcwd()
            schedule_filename = filedialog.askopenfilename(initialdir=initial_dir, title="Load Schedule",
                                                          filetypes=(("Schedule", "*.json"),))
            if schedule_filename:
                with open(schedule_filename, 'r') as file:
                    json_text = file.read()
                    self.frames[ScheduleEditor].schedule.load_from_json_string(json_text)
                    self.frames[ScheduleEditor].refresh_periods_lb()
                self.last_schedule_directory = os.path.dirname(schedule_filename)
        except (IntervalTimerException, IOError) as e:
            messagebox.showerror('Open Schedule Error', e)

    def on_save_schedule(self):
        try:
            if self.last_schedule_directory:
                initial_dir = self.last_schedule_directory
            else:
                initial_dir = os.getcwd()
            schedule_filename = filedialog.asksaveasfilename(initialdir=initial_dir, title="Save Schedule",
                                                            filetypes=(("Schedule", "*.json"),),
                                                            defaultextension='.json')
            if schedule_filename:
                with open(schedule_filename, 'w') as file:
                    json_text = self.frames[ScheduleEditor].schedule.get_schedule_json_string()
                    file.write(json_text)
                self.last_schedule_directory = os.path.dirname(schedule_filename)
        except (IntervalTimerException, IOError) as e:
            messagebox.showerror('Open Schedule Error', e)


    def change_view(self):
        self.modify_interval_timer_lock.acquire()
        if self.view_menu_option.get() == 1:
            if self.frames[IntervalTimer]:
                # Clear interval timer out
                self.prefs_dict['interval_timer_prefs'] = self.frames[IntervalTimer].get_prefs_as_dict()
                self.frames[IntervalTimer].grid_forget()
                self.frames[IntervalTimer].destroy()
                self.frames[IntervalTimer] = None
            self.current_frame = self.frames[ScheduleEditor]
        elif self.view_menu_option.get() == 2:
            if len(self.frames[ScheduleEditor].schedule.periods) >= 1:
                # Set up interval timer script
                interval_timer_script = schedule_to_interval_timer_script(self.frames[ScheduleEditor].schedule,
                                                                          self.prefs_dict['announcement_time_prefs'])
                self.frames[IntervalTimer] = IntervalTimer(self.mainframe, interval_timer_script, self.media_interface,
                                                           self.prefs_dict['interval_timer_prefs'])
                self.frames[IntervalTimer].grid(row=0, column=0, sticky='NSEW')
                self.frames[IntervalTimer].announcement_callback = self.announcement_handler
                self.current_frame = self.frames[IntervalTimer]
            else:
                messagebox.showerror('Interval Timer Error', 'Script must have at least one period.')
                self.view_menu_option.set(1)
        self.modify_interval_timer_lock.release()
        self.current_frame.tkraise()


    def on_close(self):
        self.prefs_dict['schedule_prefs'] = {}
        self.prefs_dict['schedule_prefs']['last_schedule_directory'] = self.last_schedule_directory
        if self.frames[IntervalTimer] != None:
            self.prefs_dict['interval_timer_prefs'] = self.frames[IntervalTimer].get_prefs_as_dict()
        try:
            save_prefs(self.prefs_dict, os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'prefs.json'))
        except IntervalTimerException:
            messagebox.showerror('Save Preferences Error', 'Couldn\'t save preferences')

        self.destroy()

    def handle_message(self, message):
        print('message: ' + message)
        self.modify_interval_timer_lock.acquire()
        message = message.strip().upper()
        if message == 'PAUSE_MEDIA' and self.media_interface:
            self.media_interface.pause()
            response = 'Pause Media\n'
        elif message == 'SKIP_SONG' and self.media_interface:
            self.media_interface.skip_song()
            response = 'Skip Song\n'
        elif message == 'MEDIA_VOL_DOWN':
            self.media_interface.vol_down()
            response = 'Vol Down\n'
        elif message == 'MEDIA_VOL_UP':
            self.media_interface.vol_up()
            response = 'Vol Down\n'
        elif self.frames[IntervalTimer]:
            if message == 'PAUSE_TIMER':
                self.frames[IntervalTimer].pause_timer()
                response = 'Pause Timer\n'
            elif message == 'ADD_10':
                self.frames[IntervalTimer].add_time_remaining_in_period(10)
                response = 'Added 10 seconds\n'
            elif message == 'ADD_30':
                self.frames[IntervalTimer].add_time_remaining_in_period(30)
                response = 'Added 30 seconds\n'
            elif message == 'REMOVE_10':
                self.frames[IntervalTimer].add_time_remaining_in_period(-10)
                response = 'Removed 10 seconds\n'
            elif message == 'REMOVE_30':
                self.frames[IntervalTimer].add_time_remaining_in_period(-30)
                response = 'Removed 30 seconds\n'
            elif message == 'PERIOD_TIME':
                period, time = self.frames[IntervalTimer].get_period_time_remaining_lbl_values()
                response = f'{period}    {time}\n'
            elif message == 'NEXT_PERIOD':
                self.frames[IntervalTimer].next_period()
                response = 'Next period\n'
            elif message == 'PREVIOUS_PERIOD':
                self.frames[IntervalTimer].previous_period()
                response = 'Previous period\n'
            else:
                response = 'Unrecognized Command\n'
        else:
            response = 'Interval Timer Not Active\n'
        self.modify_interval_timer_lock.release()
        return response



if __name__=='__main__':
    prefs, load_pref_errors = load_prefs(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'prefs.json'))

    # Attempt to load up music library.
    try:
        if prefs['music_library_prefs']['music_library_path']:
            music_library = ml.load_library(prefs['music_library_prefs']['music_library_path'])
        else:
            music_library = None
    except (FileNotFoundError, IOError):
        music_library = None

    # Attempt to load up vlc and wire the announcement handler
    try:
        vlc_connection = VLCConnection(prefs['vlc_prefs']['vlc_path'])
        if music_library:
            vlc_music_manager = AutomaticVLCMusicManager(vlc_connection, lambda: ml.get_random_song_path_from_library(music_library))
        else:
            vlc_music_manager = VLCMusicManager(vlc_connection)
        vlc_connection.vlc_message_callback = vlc_music_manager.receive_vlc_messages
        vlc_loaded = True
    except FileNotFoundError:
        vlc_loaded = False
        vlc_connection = None
        vlc_music_manager = None
    sound_manager = SoundManager('sounds', vlc_music_manager)
    announcement_handler = AnnouncementTimeHandler(sound_manager)

    # Set up interface to allow clients to send messages to this program
    remote_tcp_interface = TCPInterface()
    remote_address = f'Listening locally at: {remote_tcp_interface.host_ip} : {remote_tcp_interface.port}'

    # Set up app
    root = App(prefs, announcement_handler.handle_script_announcements, vlc_music_manager, remote_address)
    remote_tcp_interface.message_callback = root.handle_message

    if load_pref_errors:
        messagebox.showerror('Load preference errors', load_pref_errors)
    if not vlc_loaded:
        messagebox.showerror('Connect to VLC Error', 'Couldn\'t connect to VLC')
    if not music_library:
        messagebox.showerror('Music Library Error', 'Couldn\'t load a music libary.')

    def on_close():
        if vlc_connection:
            vlc_connection.vlc_subprocess.kill()
        if music_library:
            ml.save_library(music_library, prefs['music_library_prefs']['music_library_path'])
        root.on_close()

    root.state('zoomed')
    root.protocol('WM_DELETE_WINDOW', on_close)
    root.mainloop()
