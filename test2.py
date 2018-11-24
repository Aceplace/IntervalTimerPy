import re

message = 'audio volume: 307'

match = re.search(r'audio volume: \d*', message)
if match:
    print(match.group(0))
else:
    print('no match')