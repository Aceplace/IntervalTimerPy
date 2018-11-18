import json
import schedule

class PeriodAnnouncementPrefs:
    def __init__(self):
        self.period_announcement_times = {}
        for length in range(1, schedule.Schedule.MAX_PERIOD_LENGTH):
            self.period_announcement_times[length] = []

    def export_to_json(self, file_name):
        with open(file_name, 'w') as file:
            json.dump(self.period_announcement_times, file, indent=4)

    def load_from_json(self, file_name):
        with open(file_name, 'r') as file:
            period_announcment_times_string_keys = json.load(file)
            period_announcment_times_int_keys = {int(key):value for (key,value) in period_announcment_times_string_keys.items()}
            self.period_announcement_times = period_announcment_times_int_keys


if __name__=='__main__':
    prefs = PeriodAnnouncementPrefs()
    print(prefs.period_announcement_times)
    #prefs.export_to_json('announcementprefs.json')
    prefs.load_from_json('announcementprefs.json')
    print(prefs.period_announcement_times)