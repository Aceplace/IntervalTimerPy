import tkinter as tk
import json
import intervaltimer.periodannouncementadapter as paadapt
from tkinter import messagebox

from intervaltimer.intervaltimer import IntervalTimer
from intervaltimer.scheduleintervaltimeradapter import schedule_to_interval_timer_script
from misc.intervaltimerexception import IntervalTimerException
from intervaltimer.periodannouncementadapter import PeriodAnnouncementAdapter
from schedule.scheduleeditor import ScheduleEditor
from schedule.scheduleeditorcontroller import ScheduleEditorController
from sounds.announcementtimehandler import AnnouncementTimeHandler
from sounds.soundmanager import SoundManager


class App(tk.Tk):
    def __init__(self, announcement_handler, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self.announcement_handler = announcement_handler

        #load up preferences
        try:
            with open('prefs.json', 'r') as file:
                prefs_dict = json.load(file)
        except (IOError, json.decoder.JSONDecodeError) as e:
            messagebox.showerror('Load Preferences Error', str(e))

        self.prefs_dict = {}
        try:
            self.prefs_dict['interval_timer_prefs'] = prefs_dict['interval_timer_prefs']
        except KeyError:
            messagebox.showerror('Load Preferences Error', 'Couldn\'t load interval timer preferences.')
            self.prefs_dict['interval_timer_prefs'] = None

        try:
            announcement_time_prefs_string_keys = prefs_dict['announcement_time_prefs']
            self.prefs_dict['announcement_time_prefs'] = paadapt.convert_to_interval_timer_period_announcement_times(announcement_time_prefs_string_keys)
        except KeyError:
            messagebox.showerror('Load Preferences Error', 'Couldn\'t load announcement time preferences')
            self.prefs_dict['announcement_time_prefs'] = paadapt.get_default_interval_timer_period_announcement_times()

        #menu setup
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

        #frame set ups
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
        if self.viewmenu_option.get() == 1:
            if self.frames[IntervalTimer]:
                #self.save_interval_timer_prefs()
                self.prefs_dict['interval_timer_prefs'] = self.frames[IntervalTimer].get_prefs_as_dict()
                self.frames[IntervalTimer].grid_forget()
                self.frames[IntervalTimer].destroy()
                self.frames[IntervalTimer] = None
            self.current_frame = self.frames[ScheduleEditor]
        elif self.viewmenu_option.get() == 2:
            if len(self.schedule_editor_controller.schedule.periods) >= 1:
                self.setup_interval_timer()
                self.current_frame = self.frames[IntervalTimer]
            else:
                messagebox.showerror('Interval Timer Error', 'Script must have at least one period.')
                self.viewmenu_option.set(1)

        self.current_frame.tkraise()

    def setup_interval_timer(self):
        interval_timer_script = schedule_to_interval_timer_script(self.schedule_editor_controller.schedule, self.prefs_dict['announcement_time_prefs'])
        #try:
        #    with open('intervaltimerprefs.json', 'r') as file:
        #        prefs_dict = json.load(file)
        #except (IOError, json.decoder.JSONDecodeError) as e:
        #    messagebox.showerror('Load preferences error', 'Preferences file format error: ' + str(e))
        #    prefs_dict = None

        self.frames[IntervalTimer] = IntervalTimer(self.mainframe, interval_timer_script, self.prefs_dict['interval_timer_prefs'])
        self.frames[IntervalTimer].grid(row=0, column=0, sticky='NSEW')
        self.frames[IntervalTimer].announcement_callback = self.announcement_handler

    def save_interval_timer_prefs(self):
        try:
            with open('intervaltimerprefs.json', 'w') as file:
                prefs_dict = self.frames[IntervalTimer].get_prefs_as_dict()
                json.dump(prefs_dict, file)
        except IntervalTimerException as e:
            messagebox.showerror('Save Preferences Error', 'Couldn\'t save interval timer preferences.')

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


sound_manager = SoundManager('sounds')
anouncement_handler = AnnouncementTimeHandler(sound_manager)

root = App(anouncement_handler.handle_script_announcements)
root.state('zoomed')
root.protocol('WM_DELETE_WINDOW', root.on_close)
root.mainloop()