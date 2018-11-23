import tkinter as tk
import json

# Expected Script Format
# List of Periods
# Each Period -> {'length': , 'period number', 'period announcement times'}
from misc.intervaltimerexception import IntervalTimerException


def seconds_to_minutes_seconds_string(num_seconds):
    num_minutes_string = str(num_seconds // 60)
    num_seconds_string = str(num_seconds % 60) if num_seconds % 60 >= 10 else '0' + str(num_seconds % 60)
    return f'{num_minutes_string}:{num_seconds_string}'


class IntervalTimer(tk.Frame):
    def __init__(self, root, script, prefs=None):
        super(IntervalTimer, self).__init__(root)
        self.script = script
        self.current_period = 0
        self.time_remaining_in_period = 0
        self.is_playing = False
        self.period_lbl_size = 240 if not prefs else prefs['period_lbl_size']
        self.time_lbl_two_digit_size = 330 if not prefs else prefs['time_lbl_two_digit_size']
        self.time_lbl_one_digit_size = 370 if not prefs else prefs['time_lbl_one_digit_size']
        self.announcement_callback = None

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        interval_timer_playback_frame = tk.Frame(self)
        interval_timer_playback_frame.grid_columnconfigure(3, weight=1)
        self.previous_period_btn = tk.Button(interval_timer_playback_frame, text='<<', command=self.previous_period)
        self.previous_period_btn.grid(row=0, column=0, sticky='W')
        tk.Button(interval_timer_playback_frame, text='>', command=self.play_pause).grid(row=0, column=1, sticky='W')
        self.next_period_btn = tk.Button(interval_timer_playback_frame, text='>>', command=self.next_period)
        self.next_period_btn.grid(row=0, column=2, sticky='W')
        self.interval_timer_slider = tk.Scale(interval_timer_playback_frame, from_=0, to_=1800, showvalue=False, orient=tk.HORIZONTAL, command=self.slider_update)
        self.interval_timer_slider.grid(row=1, column=0, columnspan=4, stick='WE')
        interval_timer_playback_frame.grid(row=0, column=0, sticky='NSEW')

        lbls_parent_frame = tk.Frame(self)
        lbls_parent_frame.grid(row=1, column=0, columnspan=2, sticky='NSEW')
        lbls_parent_frame.grid_rowconfigure(0, weight=1)
        lbls_parent_frame.grid_columnconfigure(1, weight=1)

        period_lbl_frame = tk.Frame(lbls_parent_frame)
        period_lbl_frame.grid_rowconfigure(1, weight=1)
        tk.Button(period_lbl_frame, text='Decrease Period Size', command=self.decrease_period_lbl_size).grid(row=0, column=0, stick='NW')
        tk.Button(period_lbl_frame, text='Increase Period Size', command=self.increase_period_lbl_size).grid(row=0, column=1, stick='NW')
        self.period_lbl = tk.Label(period_lbl_frame, text='10', font=('Times', self.period_lbl_size))
        self.period_lbl.grid(row=1, column=0, columnspan=2, sticky='SW')
        period_lbl_frame.grid(row=0, column=0, sticky='NSEW')

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

        if self.script:
            self.time_remaining_in_period = self.script[self.current_period]['length']
            self.period_lbl.configure(text=self.script[self.current_period]['period number'])
            self.time_lbl.configure(text=seconds_to_minutes_seconds_string(self.time_remaining_in_period), font=('Times', self.get_time_label_size_for_time_remaining()))
            self.interval_timer_slider.configure(to_= self.time_remaining_in_period - 1)
            self.interval_timer_slider.set(0)


        self.after(1000, self.on_second)

    def on_second(self):
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

        if self.script:
            self.time_lbl.configure(text=seconds_to_minutes_seconds_string(self.time_remaining_in_period), font=('Times', self.get_time_label_size_for_time_remaining()))
            self.interval_timer_slider.configure(state=tk.NORMAL)
            self.interval_timer_slider.set(self.script[self.current_period]['length'] - self.time_remaining_in_period)
            if self.is_playing:
                self.interval_timer_slider.configure(state=tk.DISABLED)
        self.after(1000, self.on_second)

    def previous_period(self):
        self.current_period -= 1
        if self.current_period < 0:
            self.current_period = len(self.script) - 1
        self.time_remaining_in_period = self.script[self.current_period]['length']
        self.interval_timer_slider.configure(to_=self.time_remaining_in_period - 1)
        self.interval_timer_slider.set(0)
        self.period_lbl.configure(text=self.script[self.current_period]['period number'])
        self.time_lbl.configure(text=seconds_to_minutes_seconds_string(self.time_remaining_in_period), font=('Times', self.get_time_label_size_for_time_remaining()))

    def next_period(self):
        self.current_period += 1
        if self.current_period >= len(self.script):
            self.current_period = 0
        self.time_remaining_in_period = self.script[self.current_period]['length']
        self.interval_timer_slider.configure(to_=self.time_remaining_in_period - 1)
        self.interval_timer_slider.set(0)
        self.period_lbl.configure(text=self.script[self.current_period]['period number'])
        self.time_lbl.configure(text=seconds_to_minutes_seconds_string(self.time_remaining_in_period), font=('Times', self.get_time_label_size_for_time_remaining()))

    def play_pause(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.interval_timer_slider.configure(state=tk.DISABLED)
            self.previous_period_btn.configure(state=tk.DISABLED)
            self.next_period_btn.configure(state=tk.DISABLED)
        else:
            self.interval_timer_slider.configure(state=tk.NORMAL)
            self.previous_period_btn.configure(state=tk.NORMAL)
            self.next_period_btn.configure(state=tk.NORMAL)

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
        return self.time_lbl_two_digit_size if len(seconds_to_minutes_seconds_string(self.time_remaining_in_period)) == 5 else self.time_lbl_one_digit_size

    def slider_update(self, new_slider_value):
        self.time_remaining_in_period = self.script[self.current_period]['length'] - int(new_slider_value)
        self.time_lbl.configure(text=seconds_to_minutes_seconds_string(self.time_remaining_in_period), font=('Times', self.get_time_label_size_for_time_remaining()))

    def load_prefs(self, prefs):
        self.period_lbl_size = prefs['period_lbl_size']
        self.time_lbl_one_digit_size = prefs['time_lbl_one_digit_size']
        self.time_lbl_two_digit_size = prefs['time_lbl_two_digit_size']
        self.time_lbl.configure(font=('Times', self.get_time_label_size_for_time_remaining()))
        self.period_lbl.configure(font=('Times',self.period_lbl_size))

    def get_prefs_as_dict(self):
        prefs_dict = {'period_lbl_size': self.period_lbl_size,
                      'time_lbl_one_digit_size': self.time_lbl_one_digit_size,
                      'time_lbl_two_digit_size': self.time_lbl_two_digit_size}

        return prefs_dict


