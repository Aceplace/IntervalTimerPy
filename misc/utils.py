def half_minutes_to_seconds(half_minutes):
    return half_minutes * 30

def half_minutes_to_min_sec_str(half_minutes):
    minutes = half_minutes // 2
    minutes_string = str(minutes)
    extra_half_minute = half_minutes % 2
    extra_half_minute_string = '00' if extra_half_minute == 0 else '30'
    return f'{minutes_string}:{extra_half_minute_string}'

def minutes_to_hr_min_sec_str(num_minutes):
    hours = num_minutes // 120
    minutes = (num_minutes - 120 * hours) // 2
    extra_half_minute = (num_minutes - 120 * hours) % 2
    hours_string = str(hours)
    minutes_string = '0' + str(minutes) if minutes < 10 else str(minutes)
    extra_half_minute_string = '00' if extra_half_minute == 0 else '30'
    return f'{hours_string}:{minutes_string}:{extra_half_minute_string}'

def min_sec_str_to_half_minutes(min_sec_str):
    parsed_period_length_string = min_sec_str.split(':')
    num_minutes = int(parsed_period_length_string[0])
    extra_half_minute = 1 if parsed_period_length_string[1] == '30' else 0
    num_half_minutes = num_minutes * 2 + extra_half_minute
    return num_half_minutes


def seconds_to_minutes_seconds_string(num_seconds):
    num_minutes_string = str(num_seconds // 60)
    num_seconds_string = str(num_seconds % 60) if num_seconds % 60 >= 10 else '0' + str(num_seconds % 60)
    return f'{num_minutes_string}:{num_seconds_string}'