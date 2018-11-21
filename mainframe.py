import tkinter as tk
from tkinter import messagebox

from intervaltimer.intervaltimer import IntervalTimer
from intervaltimer.scheduleintervaltimeradapter import schedule_to_interval_timer_script
from misc.intervaltimerexception import IntervalTimerException
from schedule.periodannouncementprefs import PeriodAnnouncementPrefs
from schedule.scheduleeditor import ScheduleEditor
from schedule.scheduleeditorcontroller import ScheduleEditorController


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

        self.announcement_time_prefs = PeriodAnnouncementPrefs()
        try:
            self.announcement_time_prefs.load_from_json('announcementprefs.json')
        except IntervalTimerException as e:
            messagebox.showerror('Load Preferences Error', 'Couldn\'t load announcement time preferences')

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
                try:
                    self.frames[IntervalTimer].save_interval_timer_prefs('intervaltimerprefs.json')
                except IntervalTimerException as e:
                    messagebox.showerror('Save Preferences Error', 'Couldn\'t save interval timer preferences.')

                self.frames[IntervalTimer].grid_forget()
                self.frames[IntervalTimer].destroy()
                self.frames[IntervalTimer] = None
            self.current_frame = self.frames[ScheduleEditor]
        elif self.viewmenu_option.get() == 2:
            if len(self.schedule_editor_controller.schedule.periods) >= 1:
                interval_timer_script = schedule_to_interval_timer_script(self.schedule_editor_controller.schedule, self.announcement_time_prefs)
                self.frames[IntervalTimer] = IntervalTimer(self.mainframe, interval_timer_script)
                self.frames[IntervalTimer].grid(row=0, column=0, sticky='NSEW')
                self.frames[IntervalTimer].load_interval_timer_prefs('intervaltimerprefs.json')
                self.current_frame = self.frames[IntervalTimer]
            else:
                messagebox.showerror('Interval Timer Error', 'Script must have at least one period.')
                self.viewmenu_option.set(1)

        self.current_frame.tkraise()

    def on_close(self):
        self.destroy()


root = App()
root.state('zoomed')
root.protocol('WM_DELETE_WINDOW', root.on_close)
root.mainloop()