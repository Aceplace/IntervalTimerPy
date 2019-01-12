
class AnnouncementTimeHandler:
    def __init__(self, sound_manager):
        self.sound_manager = sound_manager

    def handle_script_announcements(self, current_period, time_remaining_in_period, script):
        if time_remaining_in_period - 2 in script[current_period]['announcement times']:
            if time_remaining_in_period - 2 != 5:
                sounds = ['fade_out',self.sound_manager.misc_sounds['beepthree'], self.sound_manager.time_remaining_sounds[(time_remaining_in_period - 2) // 30], 'fade_in']
                times = [0.0, 2.0, 4.5, 6.0]
            else:
                if current_period < len(script) - 1:
                    index = script[current_period + 1]['period number']
                else:
                    index = -1
                if index != -1:
                    next_period_announcement = self.sound_manager.period_sounds[index]
                else:
                    next_period_announcement = self.sound_manager.misc_sounds['endofscript']
                sounds = ['fade_out',
                          self.sound_manager.time_remaining_sounds[0],
                          self.sound_manager.misc_sounds['boxingbell'],
                          next_period_announcement,
                          ]
                times = [0.0, 2.0, 7.0, 10.0]
                if index != -1:
                    time_in_next_period = script[current_period + 1]['length']
                    sounds.extend([self.sound_manager.time_remaining_sounds[time_in_next_period // 30], 'fade_in'])
                    times.extend([11.5, 12.5])
                else:
                    sounds.extend(['fade_in'])
                    times.extend([11.5])

            self.sound_manager.play_sounds_in_sequence(sounds, times)




