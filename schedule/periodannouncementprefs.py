import json
from schedule import schedule
from misc.intervaltimerexception import IntervalTimerException


class PeriodAnnouncementPrefs:
    def __init__(self):
        self.period_announcement_times = {}
        for length in range(1, schedule.Schedule.MAX_PERIOD_LENGTH + 1):
            self.period_announcement_times[length] = []

    def export_to_json(self, file_name):
        with open(file_name, 'w') as file:
            json.dump(self.period_announcement_times, file, indent=4)

    def load_from_json(self, file_name):
        try:
            with open(file_name, 'r') as file:
                period_announcment_times_string_keys = json.load(file)
                period_announcment_times_int_keys = {int(key):value for (key,value) in period_announcment_times_string_keys.items()}
                self.period_announcement_times = period_announcment_times_int_keys
        except (IOError, json.decoder.JSONDecodeError) as e:
            raise IntervalTimerException(f'Error loading preferences:{str(e)}')

    def __getitem__(self, item):
        return self.period_announcement_times[item]


if __name__=='__main__':
    prefs = PeriodAnnouncementPrefs()
    print(prefs.period_announcement_times)
    prefs.load_from_json('announcementprefs.json')
    print(prefs.period_announcement_times)