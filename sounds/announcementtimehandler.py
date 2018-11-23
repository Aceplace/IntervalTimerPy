
class AnnouncementTimeHandler:
    def __init__(self, sound_manager):
        self.sound_manager = sound_manager

    def handle_script_announcements(self, current_period, time_remaining_in_period, script):
        if time_remaining_in_period in script[current_period]['announcement times']:
            if time_remaining_in_period != 5:
                sounds = [self.sound_manager.misc_sounds['beepthree'], self.sound_manager.time_remaining_sounds[time_remaining_in_period // 30]]
                times = [0.0, 2.5]
            else:
                if current_period < len(script) - 1:
                    index = script[current_period + 1]['period number']
                else:
                    index = -1
                if index != -1:
                    next_period_announcement = self.sound_manager.period_sounds[index]
                else:
                    next_period_announcement = self.sound_manager.misc_sounds['endofscript']
                sounds = [self.sound_manager.time_remaining_sounds[0],
                          self.sound_manager.misc_sounds['boxingbell'],
                          next_period_announcement]
                times = [0.0, 5.0, 8.0]
                if index != -1:
                    time_in_next_period = script[current_period + 1]['length']
                    sounds.append(self.sound_manager.time_remaining_sounds[time_in_next_period // 30])
                    times.append(9.0)

            self.sound_manager.play_sounds_in_sequence(sounds, times)




