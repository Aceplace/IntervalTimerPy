def schedule_to_interval_timer_script(schedule, period_announcment_prefs):
    script = []
    for period_length in schedule.periods:
        script.append({'length':period_length * 30})
        script[len(script) - 1]['period number'] = len(script) if not schedule.does_include_period_zero else len(script) - 1
        script[len(script) - 1]['announcement times'] = [to_seconds(announcement_time) for announcement_time in period_announcment_prefs[period_length]]
    return script

def to_seconds(half_minutes):
    if half_minutes == 0:
        return 5
    return half_minutes * 30

if __name__=='__main__':
    from schedule.schedule import Schedule
    from intervaltimer.periodannouncementprefs import PeriodAnnouncementPrefs
    schedule = Schedule()
    schedule.periods = [20, 20, 20, 60]
    announcement_prefs = PeriodAnnouncementPrefs()
    announcement_prefs.load_from_json('announcementprefs.json')

    script = schedule_to_interval_timer_script(schedule, announcement_prefs)
    print(script)