import json
from schedule import schedule
from misc.intervaltimerexception import IntervalTimerException

def convert_to_interval_timer_period_announcement_times(period_announcement_times_string_keys):
    return {int(key):value for (key,value) in period_announcement_times_string_keys.items()}

def get_default_interval_timer_period_announcement_times():
    period_announcement_times = {}
    for length in range(1, schedule.Schedule.MAX_PERIOD_LENGTH + 1):
        period_announcement_times[length] = []
    return period_announcement_times
