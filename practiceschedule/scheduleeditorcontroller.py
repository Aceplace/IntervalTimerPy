from misc.utils import half_minutes_to_min_sec_str
from practiceschedule.schedule import Schedule


class ScheduleEditorController:
    def __init__(self):
        self.schedule = Schedule()

    def get_periods_as_strings(self):
        period_strings = []

        for index in range(0, len(self.schedule.periods)):
            period_length_string = half_minutes_to_min_sec_str(self.schedule.periods[index])
            period_number_string = str(index) if self.schedule.does_include_period_zero else str(index + 1)
            spaces = '      ' if len(period_number_string) == 1 else '    '
            period_strings.append(f'{period_number_string}{spaces}{period_length_string}')

        return period_strings

    def remove_period_by_index(self, index):
        self.schedule.remove_period(index)

    def add_period_at_index(self, index, period_length):
        self.schedule.add_period_at_index(index, period_length)

    def set_does_include_period_zero(self, does_include_period_zero):
        self.schedule.does_include_period_zero = does_include_period_zero

    def get_does_include_period_zero(self):
        return self.schedule.does_include_period_zero

    def get_total_length_string(self):
        total_length = self.schedule.get_total_length()
        total_length_string = Schedule.minutes_to_hr_min_sec_str(total_length)
        return total_length_string
