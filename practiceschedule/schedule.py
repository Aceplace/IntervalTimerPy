from misc.intervaltimerexception import IntervalTimerException
import json

#time units are half-minutes
class Schedule:
    MAX_NUMBER_OF_PERIODS = 40
    MAX_PERIOD_LENGTH = 60

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

