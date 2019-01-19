import os
import tkinter as tk
import sys
import traceback
from collections import namedtuple

import threading
import mediaplayer.musiclibrary as ml
from tkinter import messagebox

from intervaltimer.intervaltimer import IntervalTimer
from intervaltimer.adapters import schedule_to_interval_timer_script
from intervaltimer.tcpinterface import TCPInterface
from mediaplayer.automaticvlcmusicmanager import AutomaticVLCMusicManager
from mediaplayer.vlcconnection import VLCConnection
from mediaplayer.vlcmusicmanager import VLCMusicManager
from misc.intervaltimerexception import IntervalTimerException
from prefs import save_prefs, load_prefs
from soundmanager.announcementtimehandler import AnnouncementTimeHandler
from soundmanager.soundmanager import SoundManager


class RemoteMessageHandler:
    def __init__(self, interval_timer, media_interface):
        self.media_interface = media_interface
        self.interval_timer = interval_timer
        self.modify_interval_timer_lock = threading.Lock()

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
        elif self.interval_timer:
            if message == 'PAUSE_TIMER':
                self.interval_timer.pause_timer()
                response = 'Pause Timer\n'
            elif message == 'ADD_10':
                self.interval_timer.add_time_remaining_in_period(10)
                response = 'Added 10 seconds\n'
            elif message == 'ADD_30':
                self.interval_timer.add_time_remaining_in_period(30)
                response = 'Added 30 seconds\n'
            elif message == 'REMOVE_10':
                self.interval_timer.add_time_remaining_in_period(-10)
                response = 'Removed 10 seconds\n'
            elif message == 'REMOVE_30':
                self.interval_timer.add_time_remaining_in_period(-30)
                response = 'Removed 30 seconds\n'
            elif message == 'PERIOD_TIME':
                period, time = self.interval_timer.get_period_time_remaining_lbl_values()
                response = f'{period}    {time}\n'
            elif message == 'NEXT_PERIOD':
                self.interval_timer.next_period()
                response = 'Next period\n'
            elif message == 'PREVIOUS_PERIOD':
                self.interval_timer.previous_period()
                response = 'Previous period\n'
            else:
                response = 'Unrecognized Command\n'
        else:
            response = 'Interval Timer Not Active\n'
        self.modify_interval_timer_lock.release()
        return response

# Assumes one properly formatted text file in directory
def get_file_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.read().splitlines()

    # Clean the list removing blank spaces and white spaces
    lines = [line.strip() for line in lines if line.strip() != '']

    return lines


def parse_file_lines(lines):
    script = {'does_include_period_zero':False,
              'periods':[]}

    if len(lines) == 0 or len(lines) == 1:
        raise Exception('Must have at least two lines.')

    if lines[0].upper() == 'YES':
        script['does_include_period_zero'] = True
    elif lines[0].upper() == 'NO':
        script['does_include_period_zero'] = False
    else:
        raise Exception('First line must be "Yes" or "No"')


    for i, line in enumerate(lines):
        if i == 0:
            continue

        period_time_strings = line.split()
        for j, period_time_string in enumerate(period_time_strings):
            min_sec = period_time_string.split(':')
            if len(min_sec) != 1 and len(min_sec) != 2:
                raise Exception('Incorrectly formatted period times')

            try:
                if len(min_sec) == 1:
                    period_time = int(min_sec[0]) * 2
                else:
                    if min_sec[1] != '30':
                        raise Exception('Incorrectly formatted period times')
                    period_time = int(min_sec[0]) * 2 + 1

                if period_time == 0:
                    raise Exception('Incorrectly formatted period times')

                script['periods'].append(period_time)
            except ValueError:
                raise Exception('Incorrectly formatted period times')

    return script

if __name__=='__main__':

    try:
        prefs, load_pref_errors = load_prefs(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'prefs.json'))
        if load_pref_errors:
            print(load_pref_errors)

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
                vlc_music_manager = AutomaticVLCMusicManager(vlc_connection,
                                                             lambda: ml.get_random_song_path_from_library(music_library),
                                                             prefs['vlc_prefs']['fade_to_volume'])
            else:
                vlc_music_manager = VLCMusicManager(vlc_connection, prefs['vlc_prefs']['fade_to_volume'])
            vlc_connection.vlc_message_callback = vlc_music_manager.receive_vlc_messages
            vlc_loaded = True
        except FileNotFoundError:
            vlc_loaded = False
            vlc_connection = None
            vlc_music_manager = None
        sound_manager = SoundManager(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'sounds'), vlc_music_manager)
        announcement_handler = AnnouncementTimeHandler(sound_manager)

        # Set up interface to allow clients to send messages to this program
        remote_tcp_interface = TCPInterface()
        remote_address = f'Listening locally at: {remote_tcp_interface.host_ip} : {remote_tcp_interface.port}'

        # Open up schedule script
        parsed_schedule = parse_file_lines(get_file_lines(sys.argv[1]))
        ScheduleScript = namedtuple('ScheduleScript', 'periods does_include_period_zero')
        schedule_script = ScheduleScript(periods=parsed_schedule['periods'],
                                         does_include_period_zero=parsed_schedule['does_include_period_zero'])
        timer_script = schedule_to_interval_timer_script(schedule_script,
                                                         prefs['announcement_time_prefs'])

        # Set up quick launch interval timer app
        root = tk.Tk()

        interval_timer = IntervalTimer(root, timer_script, vlc_music_manager, prefs['interval_timer_prefs'])
        interval_timer.pack(fill=tk.BOTH, expand=True)
        tk.Label(text=remote_address).pack()
        interval_timer.announcement_callback = announcement_handler.handle_script_announcements

        remote_message_handler = RemoteMessageHandler(interval_timer, vlc_music_manager)
        remote_tcp_interface.message_callback = remote_message_handler.handle_message


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

            prefs['interval_timer_prefs'] = interval_timer.get_prefs_as_dict()
            try:
                save_prefs(prefs, os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'prefs.json'))
            except IntervalTimerException:
                messagebox.showerror('Save Preferences Error', 'Couldn\'t save preferences')

            root.destroy()

        root.state('zoomed')
        root.protocol('WM_DELETE_WINDOW', on_close)
        root.mainloop()
    except:
        traceback.print_exc()
        print('Press enter to exit')
        input()

