import tkinter as tk
from schedule import schedule


class ScheduleEditor(tk.Frame):
    NUM_ITEMS_ADD_PERIOD_ROW = 10

    def __init__(self, root, controller):
        super(ScheduleEditor, self).__init__(root)
        self.controller = controller

        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        add_period_buttons_frame = tk.Frame(self)
        tk.Label(add_period_buttons_frame, text='Add Period:').grid(row=0, column=0, columnspan=ScheduleEditor.NUM_ITEMS_ADD_PERIOD_ROW, sticky='W')
        for i in range(1, schedule.Schedule.MAX_PERIOD_LENGTH + 1):
            self.create_add_period_button(add_period_buttons_frame, i)
        add_period_buttons_frame.grid(row=0, column=0, sticky='NW')

        periods_frame = tk.Frame(self)
        periods_scrollbar = tk.Scrollbar(periods_frame)
        periods_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.periods_lb = tk.Listbox(periods_frame)
        self.periods_lb.pack(fill=tk.Y, expand=True)
        self.periods_lb.configure(yscrollcommand=periods_scrollbar.set)
        periods_scrollbar.configure(command=self.periods_lb.yview)
        periods_frame.grid(row=0, column=1, sticky='NS')

        misc_items_frame = tk.Frame(self)
        delete_period_btn = tk.Button(misc_items_frame, text='Delete Period', command=self.delete_period)
        delete_period_btn.pack()
        self.include_period_zero_cb_value = tk.BooleanVar()
        self.include_period_zero_cb = tk.Checkbutton(misc_items_frame, text='Include Period Zero',
                                                     variable=self.include_period_zero_cb_value, command=self.include_period_zero_click)
        self.include_period_zero_cb_value.set(self.controller.get_does_include_period_zero())
        self.include_period_zero_cb.pack()
        self.total_length_lbl = tk.Label(misc_items_frame, text='Total Length: 0:00:00')
        self.total_length_lbl.pack()
        misc_items_frame.grid(row=0, column=2, sticky='NW')

        self.refresh_periods_lb()


    def create_add_period_button(self, parent, index):
        button = tk.Button(parent, text=schedule.Schedule.period_length_to_string(index), command=lambda:self.add_period(index))
        row = (index - 1) // ScheduleEditor.NUM_ITEMS_ADD_PERIOD_ROW + 1
        column =  (index - 1) % ScheduleEditor.NUM_ITEMS_ADD_PERIOD_ROW
        button.grid(row=row, column=column, sticky='EW')


    def delete_period(self):
        curse_selection = self.periods_lb.curselection()
        if curse_selection:
            curse_selection = curse_selection[0]
            self.controller.remove_period_by_index(curse_selection)
            self.refresh_periods_lb()
            if curse_selection >= self.periods_lb.size():
                curse_selection -= 1
            if curse_selection >= 0:
                self.periods_lb.selection_set(curse_selection, curse_selection)
                self.periods_lb.activate(curse_selection)


    def include_period_zero_click(self):
        self.controller.set_does_include_period_zero(self.include_period_zero_cb_value.get())


    def add_period(self, period_length):
        curse_selection = self.periods_lb.curselection()
        if curse_selection:
            index = curse_selection[0] + 1
        else:
            index = len(self.controller.schedule.periods)

        self.controller.add_period_at_index(index, period_length)
        self.refresh_periods_lb()
        self.periods_lb.selection_set(index, index)
        self.periods_lb.activate(index)


    def refresh_periods_lb(self):
        self.periods_lb.delete(0, tk.END)
        period_strings = self.controller.get_periods_as_strings()
        for period_string in period_strings:
            self.periods_lb.insert(tk.END, period_string)
        total_length_string = self.controller.get_total_length_string()
        self.total_length_lbl.configure(text=f'Total Length: {total_length_string}')






if __name__=='__main__':
    root = tk.Tk()
    from schedule.scheduleeditorcontroller import ScheduleEditorController
    controller = ScheduleEditorController()
    controller.schedule.periods = [10, 20, 40, 50, 35, 5, 5, 5, 5, 5, 5, 5]
    controller.schedule.does_include_period_zero = True
    ScheduleEditor(root, controller).pack(fill=tk.BOTH, expand=True)
    root.mainloop()





