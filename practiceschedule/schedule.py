from misc.intervaltimerexception import IntervalTimerException
import json

#time units are half-minutes
class Schedule:
    MAX_NUMBER_OF_PERIODS = 40
    MAX_PERIOD_LENGTH = 60

    @staticmethod
    def half_minutes_to_min_sec_str(num_minutes):
        num_minutes = num_minutes // 2
        num_minutes_string = str(num_minutes)
        extra_half_minute = num_minutes % 2
        extra_half_minute_string = '00' if extra_half_minute == 0 else '30'
        return f'{num_minutes_string}:{extra_half_minute_string}'

    @staticmethod
    def minutes_to_hr_min_sec_str(num_minutes):
        hours = num_minutes // 120
        minutes = (num_minutes - 120 * hours) // 2
        extra_half_minute = (num_minutes - 120 * hours) % 2
        hours_string = str(hours)
        minutes_string = '0' + str(minutes) if minutes < 10 else str(minutes)
        extra_half_minute_string = '00' if extra_half_minute == 0 else '30'
        return f'{hours_string}:{minutes_string}:{extra_half_minute_string}'


    @staticmethod
    def string_to_period_length(period_length_string):
        parsed_period_length_string = period_length_string.split(':')
        num_minutes = int(parsed_period_length_string[0])
        extra_half_minute = 1 if parsed_period_length_string[1] == '30' else 0
        num_half_minutes = num_minutes * 2 + extra_half_minute
        return num_half_minutes

    def __init__(self):
        self.periods = []
        self.does_include_period_zero = False


    def add_period(self, period_length):
        if len(self.periods) == Schedule.MAX_NUMBER_OF_PERIODS:
            raise IntervalTimerException(f'Only allowed {Schedule.MAX_NUMBER_OF_PERIODS} periods')
        if period_length < 1 or period_length >= Schedule.MAX_PERIOD_LENGTH:
            raise IntervalTimerException(f'Period length out of bounds (1 to {Schedule.MAX_PERIOD_LENGTH} half-minutes')

        self.periods.append(period_length)


    def remove_period(self, index):
        try:
            del self.periods[index]
        except IndexError:
            raise IntervalTimerException('Period doesn\'t exist.')


    def add_period_at_index(self, index, period_length):
        if len(self.periods) == Schedule.MAX_NUMBER_OF_PERIODS:
            raise IntervalTimerException(f'Only allowed {Schedule.MAX_NUMBER_OF_PERIODS} periods')
        if period_length < 1 or period_length > Schedule.MAX_PERIOD_LENGTH:
            raise IntervalTimerException(f'Period length out of bounds (0 to {Schedule.MAX_PERIOD_LENGTH} half-minutes')

        self.periods.insert(index, period_length)

    def get_total_length(self):
        total = 0
        for period in self.periods:
            total += period
        return total


    def get_schedule_json_string(self):
        return json.dumps(self.__dict__, indent=4)


    def load_from_json_string(self, json_string):
        try:
            parsed_json = json.loads(json_string)
            self.periods = parsed_json['periods']
            self.include_period_zero = parsed_json['does_include_period_zero']
        except json.decoder.JSONDecodeError as e:
            raise IntervalTimerException(f'Schedule wrongly formatted: {str(e)}')

