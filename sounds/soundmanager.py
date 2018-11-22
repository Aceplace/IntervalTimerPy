from pygame import mixer
import threading
import time

class SoundManager:
    def __init__(self):
        mixer.init()
        self.channel = mixer.Channel(0)

        #load in all the sounds into appropriate
        self.period_sounds = []
        for i in range(0, 41):
            sound_file_name = 'period' + str(i) + '.wav' if i >= 10 else 'period0' + str(i) + '.wav'
            self.period_sounds.append(mixer.Sound(sound_file_name))

        self.time_remaining_sounds = []
        for i in range(0, 61):
            if i == 0:
                sound_file_name = 'fivecountdown.wav'
            else:
                minutes_remaining_str = str(i // 2) if (i // 2) >= 10 else '0' + str(i // 2)
                seconds_remaing_str = '00' if i % 2 == 0 else '30'
                sound_file_name = f'remaining{minutes_remaining_str}{seconds_remaing_str}.wav'
            self.time_remaining_sounds.append(mixer.Sound(sound_file_name))

        self.misc_sounds = {}
        self.misc_sounds['beepthree'] = mixer.Sound('beepthree.wav')
        self.misc_sounds['boxingbell'] = mixer.Sound('boxingbell.wav')
        self.misc_sounds['endofscript'] = mixer.Sound('endofscript.wav')

    def play_sounds_in_sequence(self, sounds, times):
        thread = threading.Thread(target=self.threaded_play_sounds_at_times, args=(sounds, times))
        thread.start()

    def threaded_play_sounds_in_sequence(self, sounds, times):
        start_time = time.clock()

        elapsed_time = time.clock() - start_time
        index = 0
        while elapsed_time < times[-1]:
            elapsed_time = time.clock() - start_time
            if elapsed_time >= times[index]:
                self.channel.play(sounds[index])
                index += 1




if __name__=='__main__':
    import tkinter as tk
    root = tk.Tk()
    sound_manager = SoundManager()
    sounds = [sound_manager.time_remaining_sounds[0], sound_manager.misc_sounds['boxingbell'], sound_manager.period_sounds[6], sound_manager.time_remaining_sounds[20]]
    times = [0.0, 5.0, 8.0, 9.0]
    sound_manager.play_sounds_in_sequence(sounds, times)
    root.mainloop()

