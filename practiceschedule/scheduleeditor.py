import tkinter as tk

from misc.utils import half_minutes_to_min_sec_str
from practiceschedule.schedule import Schedule


class ScheduleEditor(tk.Frame):
    NUM_ITEMS_ADD_PERIOD_ROW = 10

    def __init__(self, root):
        super(ScheduleEditor, self).__init__(root)
        self.schedule = Schedule()

        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Set up widgets for adding periods to the schedule
        add_period_buttons_frame = tk.Frame(self)
        tk.Label(add_period_buttons_frame, text='Add Period:').grid(row=0, column=0,
                                                                    columnspan=ScheduleEditor.NUM_ITEMS_ADD_PERIOD_ROW,
                                                                    sticky='W')
        for i in range(1, Schedule.MAX_PERIOD_LENGTH + 1):
            button = tk.Button(add_period_buttons_frame, text=half_minutes_to_min_sec_str(i), command=lambda i=i:self.add_period(i))
            row = (i - 1) // ScheduleEditor.NUM_ITEMS_ADD_PERIOD_ROW + 1
            column = (i - 1) % ScheduleEditor.NUM_ITEMS_ADD_PERIOD_ROW
            button.grid(row=row, column=column, sticky='EW')
        add_period_buttons_frame.grid(row=0, column=0, sticky='NW')

        # Set up widget that displays the current schedule
        periods_frame = tk.Frame(self)
        periods_scrollbar = tk.Scrollbar(periods_frame)
        periods_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.periods_lb = tk.Listbox(periods_frame)
        self.periods_lb.pack(fill=tk.Y, expand=True)
        self.periods_lb.configure(yscrollcommand=periods_scrollbar.set)
        periods_scrollbar.configure(command=self.periods_lb.yview)
        periods_frame.grid(row=0, column=1, sticky='NS')

        # Set up widgets for misc schedule actions
        misc_items_frame = tk.Frame(self)
        delete_period_btn = tk.Button(misc_items_frame, text='Delete Period', command=self.delete_period)
        delete_period_btn.pack()
        self.include_period_zero_cb_value = tk.BooleanVar()
        self.include_period_zero_cb = tk.Checkbutton(misc_items_frame, text='Include Period Zero',
                                                     variable=self.include_period_zero_cb_value,
                                                     command=self.include_period_zero_click)
        self.include_period_zero_cb_value.set(self.schedule.does_include_period_zero)
        self.include_period_zero_cb.pack()
        self.total_length_lbl = tk.Label(misc_items_frame, text='Total Length: 0:00:00')
        self.total_length_lbl.pack()
        misc_items_frame.grid(row=0, column=2, sticky='NW')

        self.refresh_periods_lb()


    def delete_period(self):
        curse_selection = self.periods_lb.curselection()
        if curse_selection:
            curse_selection = curse_selection[0]
            self.schedule.remove_period_by_index(curse_selection)
            self.refresh_periods_lb()
            if curse_selection >= self.periods_lb.size():
                curse_selection -= 1
            if curse_selection >= 0:
                self.periods_lb.selection_set(curse_selection, curse_selection)
                self.periods_lb.activate(curse_selection)


    def include_period_zero_click(self):
        self.schedule.does_include_period_zero = self.include_period_zero_cb_value.get()


    def add_period(self, period_length):
        curse_selection = self.periods_lb.curselection()
        if curse_selection:
            index = curse_selection[0] + 1
        else:
            index = len(self.schedule.periods)

        self.schedule.add_period_at_index(index, period_length)
        self.refresh_periods_lb()
        self.periods_lb.selection_set(index, index)
        self.periods_lb.activate(index)


    def refresh_periods_lb(self):
        self.periods_lb.delete(0, tk.END)
        period_strings = self.schedule.get_periods_as_strings()
        for period_string in period_strings:
            self.periods_lb.insert(tk.END, period_string)
        total_length_string = self.schedule.get_total_length_string()
        self.total_length_lbl.configure(text=f'Total Length: {total_length_string}')






