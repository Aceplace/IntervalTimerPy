def half_minutes_to_seconds(half_minutes):
    return half_minutes * 30

def half_minutes_to_min_sec_str(num_minutes):
    num_minutes = num_minutes // 2
    num_minutes_string = str(num_minutes)
    extra_half_minute = num_minutes % 2
    extra_half_minute_string = '00' if extra_half_minute == 0 else '30'
    return f'{num_minutes_string}:{extra_half_minute_string}'