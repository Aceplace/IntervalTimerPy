import tkinter as tk
import threading
import time
from misc.utils import seconds_to_minutes_seconds_string


class IntervalTimer(tk.Frame):
    def __init__(self, root, script, media_interface, prefs):
        super(IntervalTimer, self).__init__(root)
        #Initialize interval timer values and preference values
        self.script = script
        self.current_period = 0
        self.time_remaining_in_period = 0
        self.is_playing = False
        self.media_interface = media_interface
        self.period_lbl_size = 240 if not prefs else prefs['period_lbl_size']
        self.time_lbl_two_digit_size = 330 if not prefs else prefs['time_lbl_two_digit_size']
        self.time_lbl_one_digit_size = 370 if not prefs else prefs['time_lbl_one_digit_size']
        self.announcement_callback = None
        self.affecting_timer_lock = threading.Lock()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        #Set up interval timer playback widgets
        interval_timer_playback_frame = tk.Frame(self)
        interval_timer_playback_frame.grid_columnconfigure(3, weight=1)
        self.previous_period_btn = tk.Button(interval_timer_playback_frame, text='<<', command=self.previous_period)
        self.previous_period_btn.grid(row=0, column=0, sticky='W')
        tk.Button(interval_timer_playback_frame, text='>', command=self.pause_timer).grid(row=0, column=1, sticky='W')
        self.next_period_btn = tk.Button(interval_timer_playback_frame, text='>>', command=self.next_period)
        self.next_period_btn.grid(row=0, column=2, sticky='W')
        self.interval_timer_slider = tk.Scale(interval_timer_playback_frame, from_=0, to_=1800, showvalue=False, orient=tk.HORIZONTAL, command=self.slider_update)
        self.interval_timer_slider.grid(row=1, column=0, columnspan=4, stick='WE')
        interval_timer_playback_frame.grid(row=0, column=0, sticky='NSEW')

        #Set up music playback widget
        media_playback_frame = tk.Frame(self, padx=20)
        tk.Label(media_playback_frame, text='Media Playback: ').pack(side=tk.LEFT)
        tk.Button(media_playback_frame, text='Pause', command=self.pause_media).pack(side=tk.RIGHT)
        tk.Button(media_playback_frame, text='Skip', command=self.skip_media).pack(side=tk.RIGHT)
        tk.Button(media_playback_frame, text='Vol Up', command=self.vol_up).pack(side=tk.RIGHT)
        tk.Button(media_playback_frame, text='Vol Down', command=self.vol_down).pack(side=tk.RIGHT)
        media_playback_frame.grid(row=0, column=1, sticky='E')

        #set up parent frame of the labels displaying the period number and time remaining
        lbls_parent_frame = tk.Frame(self)
        lbls_parent_frame.grid(row=1, column=0, columnspan=2, sticky='NSEW')
        lbls_parent_frame.grid_rowconfigure(0, weight=1)
        lbls_parent_frame.grid_columnconfigure(1, weight=1)

        #set up the label widget displaying the period number
        period_lbl_frame = tk.Frame(lbls_parent_frame)
        period_lbl_frame.grid_rowconfigure(1, weight=1)
        tk.Button(period_lbl_frame, text='Decrease Period Size', command=self.decrease_period_lbl_size).grid(row=0, column=0, stick='NW')
        tk.Button(period_lbl_frame, text='Increase Period Size', command=self.increase_period_lbl_size).grid(row=0, column=1, stick='NW')
        self.period_lbl = tk.Label(period_lbl_frame, text='10', font=('Times', self.period_lbl_size))
        self.period_lbl.grid(row=1, column=0, columnspan=2, sticky='SW')
        period_lbl_frame.grid(row=0, column=0, sticky='NSEW')

        #set up the widget displaying the time remaining in period
        time_lbl_frame = tk.Frame(lbls_parent_frame)
        time_lbl_frame.grid_rowconfigure(1, weight=1)
        time_lbl_frame.grid_columnconfigure(0, weight=1)
        tk.Button(time_lbl_frame, text='Decrease Time Size (Two Digit)', command=self.decrease_time_lbl_two_digit_size).grid(row=0, column=0, stick='NE')
        tk.Button(time_lbl_frame, text='Increase Time Size (Two Digit)', command=self.increase_time_lbl_two_digit_size).grid(row=0, column=1, stick='NE')
        tk.Button(time_lbl_frame, text='Decrease Time Size (One Digit)', command=self.decrease_time_lbl_one_digit_size).grid(row=0, column=2, stick='NE')
        tk.Button(time_lbl_frame, text='Increase Time Size (One Digit)', command=self.increase_time_lbl_one_digit_size).grid(row=0, column=3, stick='NE')
        self.time_lbl = tk.Label(time_lbl_frame, text='0:00', font=('Times', self.time_lbl_two_digit_size))
        self.time_lbl.grid(row=1, column=0, columnspan=4, sticky='SE')
        time_lbl_frame.grid(row=0, column=1, sticky='NSEW')

        #initialize the starting values and sizes of the label widgets
        if self.script:
            self.time_remaining_in_period = self.script[self.current_period]['length']
            self.period_lbl.configure(text=self.script[self.current_period]['period number'])
            self.time_lbl.configure(text=seconds_to_minutes_seconds_string(self.time_remaining_in_period), font=('Times', self.get_time_label_size_for_time_remaining()))
            self.interval_timer_slider.configure(to_= self.time_remaining_in_period - 1)
            self.interval_timer_slider.set(0)

        #threading.Thread(target=self.on_second, daemon=True).start()
        self.after(1000, self.on_second)

    def on_second(self):
        self.affecting_timer_lock.acquire()

        start_time = time.time()
        #decrement the time and check on changes of state. Send the time to the announcement callback for it to handle.
        if self.is_playing and self.script:
            self.time_remaining_in_period -= 1
            if self.time_remaining_in_period <= 0:
                self.current_period += 1
                if self.current_period >= len(self.script):
                    self.is_playing = False
                    self.current_period = 0
                self.time_remaining_in_period = self.script[self.current_period]['length']
                self.interval_timer_slider.configure(to_=self.time_remaining_in_period - 1)
                self.period_lbl.configure(text=str(self.script[self.current_period]['period number']))

            if self.announcement_callback:
                self.announcement_callback(self.current_period, self.time_remaining_in_period, self.script)

        #Update the slider
        if self.script:
            self.time_lbl.configure(text=seconds_to_minutes_seconds_string(self.time_remaining_in_period), font=('Times', self.get_time_label_size_for_time_remaining()))
            self.interval_timer_slider.configure(state=tk.NORMAL)
            self.interval_timer_slider.set(self.script[self.current_period]['length'] - self.time_remaining_in_period)
            if self.is_playing:
                self.interval_timer_slider.configure(state=tk.DISABLED)

        self.affecting_timer_lock.release()
        self.after(int((1.0 - ((time.time() - start_time) % 1.0)) * 1000), self.on_second)


    def previous_period(self):
        self.affecting_timer_lock.acquire()
        self.current_period -= 1
        if self.current_period < 0:
            self.current_period = len(self.script) - 1
        self.time_remaining_in_period = self.script[self.current_period]['length']
        self.interval_timer_slider.configure(to_=self.time_remaining_in_period - 1)
        self.interval_timer_slider.set(0)
        self.period_lbl.configure(text=self.script[self.current_period]['period number'])
        self.time_lbl.configure(text=seconds_to_minutes_seconds_string(self.time_remaining_in_period), font=('Times', self.get_time_label_size_for_time_remaining()))
        self.affecting_timer_lock.release()

    def next_period(self):
        self.affecting_timer_lock.acquire()
        self.current_period += 1
        if self.current_period >= len(self.script):
            self.current_period = 0
        self.time_remaining_in_period = self.script[self.current_period]['length']
        self.interval_timer_slider.configure(to_=self.time_remaining_in_period - 1)
        self.interval_timer_slider.set(0)
        self.period_lbl.configure(text=self.script[self.current_period]['period number'])
        self.time_lbl.configure(text=seconds_to_minutes_seconds_string(self.time_remaining_in_period), font=('Times', self.get_time_label_size_for_time_remaining()))
        self.affecting_timer_lock.release()

    def add_time_remaining_in_period(self, seconds_to_add):
        self.affecting_timer_lock.acquire()
        self.time_remaining_in_period += seconds_to_add
        if self.time_remaining_in_period > self.script[self.current_period]['length']:
            self.time_remaining_in_period = self.script[self.current_period]['length']
        if self.time_remaining_in_period < 1:
            self.time_remaining_in_period = 1

        self.time_lbl.configure(text=seconds_to_minutes_seconds_string(self.time_remaining_in_period),
                                font=('Times', self.get_time_label_size_for_time_remaining()))
        self.interval_timer_slider.configure(state=tk.NORMAL)
        self.interval_timer_slider.set(self.script[self.current_period]['length'] - self.time_remaining_in_period)
        if self.is_playing:
            self.interval_timer_slider.configure(state=tk.DISABLED)

        self.affecting_timer_lock.release()

    def pause_timer(self):
        self.affecting_timer_lock.acquire()
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.interval_timer_slider.configure(state=tk.DISABLED)
            self.previous_period_btn.configure(state=tk.DISABLED)
            self.next_period_btn.configure(state=tk.DISABLED)
        else:
            self.interval_timer_slider.configure(state=tk.NORMAL)
            self.previous_period_btn.configure(state=tk.NORMAL)
            self.next_period_btn.configure(state=tk.NORMAL)
        self.affecting_timer_lock.release()

    def pause_media(self):
        if self.media_interface:
            self.media_interface.pause()

    def skip_media(self):
        if self.media_interface:
            self.media_interface.skip_song()

    def vol_up(self):
        if self.media_interface:
            self.media_interface.vol_up()

    def vol_down(self):
        if self.media_interface:
            self.media_interface.vol_down()

    def decrease_period_lbl_size(self):
        self.period_lbl_size -= 10
        if self.period_lbl_size < 10 :
            self.period_lbl = 10
        self.period_lbl.configure(font=('Times', self.period_lbl_size))

    def increase_period_lbl_size(self):
        self.period_lbl_size += 10
        self.period_lbl.configure(font=('Times', self.period_lbl_size))

    def decrease_time_lbl_two_digit_size(self):
        self.time_lbl_two_digit_size -= 10
        if self.time_lbl_two_digit_size < 10:
            self.time_lbl_two_digit_size = 10
        self.time_lbl.configure(font=('Times', self.get_time_label_size_for_time_remaining()))

    def increase_time_lbl_two_digit_size(self):
        self.time_lbl_two_digit_size += 10
        self.time_lbl.configure(font=('Times', self.get_time_label_size_for_time_remaining()))

    def decrease_time_lbl_one_digit_size(self):
        self.time_lbl_one_digit_size -= 10
        if self.time_lbl_one_digit_size < 10:
            self.time_lbl_one_digit_size = 10
        self.time_lbl.configure(font=('Times', self.get_time_label_size_for_time_remaining()))

    def increase_time_lbl_one_digit_size(self):
        self.time_lbl_one_digit_size += 10
        self.time_lbl.configure(font=('Times', self.get_time_label_size_for_time_remaining()))

    def get_time_label_size_for_time_remaining(self):
        return self.time_lbl_two_digit_size if len(
            seconds_to_minutes_seconds_string(self.time_remaining_in_period)) == 5 else self.time_lbl_one_digit_size

    def slider_update(self, new_slider_value):
        self.time_remaining_in_period = self.script[self.current_period]['length'] - int(new_slider_value)
        self.time_lbl.configure(text=seconds_to_minutes_seconds_string(self.time_remaining_in_period), font=('Times', self.get_time_label_size_for_time_remaining()))


    def get_prefs_as_dict(self):
        prefs_dict = {'period_lbl_size': self.period_lbl_size,
                      'time_lbl_one_digit_size': self.time_lbl_one_digit_size,
                      'time_lbl_two_digit_size': self.time_lbl_two_digit_size}
        return prefs_dict

    def get_period_time_remaining_lbl_values(self):
        return (self.period_lbl['text'], self.time_lbl['text'])
