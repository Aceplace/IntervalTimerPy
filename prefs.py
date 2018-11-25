import json
import intervaltimer.adapters
from misc.intervaltimerexception import IntervalTimerException


def load_prefs():
    load_pref_errors = ''
    try:
        with open('prefs.json', 'r') as file:
            json_prefs_dict = json.load(file)
    except (IOError, json.decoder.JSONDecodeError) as e:
        load_pref_errors += str(e) + '\n'
        json_prefs_dict = {}
    # Convert the json dictionary to a more appropriate dictionary for the program
    prefs_dict = {}
    # Handle interval timer prefs
    try:
        prefs_dict['interval_timer_prefs'] = json_prefs_dict['interval_timer_prefs']
    except KeyError:
        load_pref_errors += str(e) + '\n'
        prefs_dict['interval_timer_prefs'] = None
    # Handle announcement time prefs
    try:
        announcement_time_prefs_string_keys = json_prefs_dict['announcement_time_prefs']
        prefs_dict['announcement_time_prefs'] = \
            intervaltimer.adapters.convert_to_interval_timer_period_announcement_times(announcement_time_prefs_string_keys)
    except KeyError:
        load_pref_errors += str(e) + '\n'
        prefs_dict['announcement_time_prefs'] = intervaltimer.adapters.get_default_interval_timer_period_announcement_times()
    # Handle vlc prefs
    try:
        prefs_dict['vlc_prefs'] = json_prefs_dict['vlc_prefs']
    except KeyError:
        load_pref_errors += str(e) + '\n'
        prefs_dict['vlc_prefs'] = {'vlc_path': '', 'fade_to_volume': 50}
    return prefs_dict, load_pref_errors


def save_prefs(prefs_dict):
    try:
        with open('prefs.json', 'w') as file:
            json.dump(prefs_dict, file, indent=4)
    except IOError as e:
        raise IntervalTimerException()