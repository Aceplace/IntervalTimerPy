from pygame import mixer
import threading
import time
import os.path

class SoundManager:
    def __init__(self, root_directory, music_controller = None):
        mixer.init()
        self.channel = mixer.Channel(0)
        self.music_controller = music_controller

        #load in all the sounds into appropriate
        self.period_sounds = []
        for i in range(0, 41):
            sound_file_name = 'period' + str(i) + '.wav' if i >= 10 else 'period0' + str(i) + '.wav'
            sound_file_name = os.path.join(root_directory, sound_file_name)
            self.period_sounds.append(mixer.Sound(sound_file_name))

        self.time_remaining_sounds = []
        for i in range(0, 61):
            if i == 0:
                sound_file_name = os.path.join(root_directory, 'fivecountdown.wav')
            else:
                minutes_remaining_str = str(i // 2) if (i // 2) >= 10 else '0' + str(i // 2)
                seconds_remaing_str = '00' if i % 2 == 0 else '30'
                sound_file_name = f'remaining{minutes_remaining_str}{seconds_remaing_str}.wav'
                sound_file_name = os.path.join(root_directory, sound_file_name)
            self.time_remaining_sounds.append(mixer.Sound(sound_file_name))

        self.misc_sounds = {}
        self.misc_sounds['beepthree'] = mixer.Sound(os.path.join(root_directory, 'beepthree.wav'))
        self.misc_sounds['boxingbell'] = mixer.Sound(os.path.join(root_directory, 'boxingbell.wav'))
        self.misc_sounds['endofscript'] = mixer.Sound(os.path.join(root_directory, 'endofscript.wav'))

    def play_sounds_in_sequence(self, sounds, times):
        thread = threading.Thread(target=self.play_sounds_in_sequence_run, args=(sounds, times), daemon=True)
        thread.start()

    def play_sounds_in_sequence_run(self, sounds, times):
        start_time = time.clock()

        elapsed_time = time.clock() - start_time
        index = 0
        while elapsed_time < times[-1]:
            elapsed_time = time.clock() - start_time
            if elapsed_time >= times[index]:
                if self.music_controller and isinstance(sounds[index], str):
                    if sounds[index] == 'fade_out':
                        self.music_controller.fade_out_music()
                    else:
                        self.music_controller.fade_in_music()
                elif not isinstance(sounds[index], str):
                    self.channel.play(sounds[index])
                index += 1


