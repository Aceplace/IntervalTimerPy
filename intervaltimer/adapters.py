from misc.utils import half_minutes_to_seconds
from practiceschedule import schedule

def schedule_to_interval_timer_script(schedule, period_announcment_prefs):
    script = []
    for period_length in schedule.periods:
        script.append({'length':period_length * 30})
        script[len(script) - 1]['period number'] = len(script) if not schedule.does_include_period_zero else len(script) - 1
        script[len(script) - 1]['announcement times'] = \
            [half_minutes_to_seconds(announcement_time) if half_minutes_to_seconds(announcement_time) != 0 else 5
             for announcement_time in period_announcment_prefs[period_length]]
            #turn 0 second announcements to 5 seconds because the program starts a countdown at that mark
    return script


def convert_to_interval_timer_period_announcement_times(period_announcement_times_string_keys):
    return {int(key):value for (key,value) in period_announcement_times_string_keys.items()}


def get_default_interval_timer_period_announcement_times():
    period_announcement_times = {}
    for length in range(1, schedule.Schedule.MAX_PERIOD_LENGTH + 1):
        period_announcement_times[length] = []
    return period_announcement_times