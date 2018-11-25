import time
import re
import threading

class VLCMusicManager:
    def __init__(self, vlc_connection):
        self.vlc_connection = vlc_connection
        self.current_volume = 0
        self.fade_to_volume = 50
        self.waiting_for_current_volume = threading.Event()

    def fade_out_music(self):
        fade_thread = threading.Thread(target=self.fade_out_music_run, daemon=True)
        fade_thread.start()

    def fade_in_music(self):
        fade_thread = threading.Thread(target=self.fade_in_music_run, daemon=True)
        fade_thread.start()

    def fade_out_music_run(self):
        self.waiting_for_current_volume.set()
        self.vlc_connection.send_message('volume')
        start_fade_time = time.clock()
        current_time = start_fade_time
        while current_time - start_fade_time < 1.5:
            time.sleep(0.01)
            current_time = time.clock()
            elapsed_time = current_time - start_fade_time
            if elapsed_time >= 1.5:
                elapsed_time = 1.5
            if not self.waiting_for_current_volume.is_set() and self.current_volume > self.fade_to_volume:
                current_fade_volume = self.current_volume - (self.current_volume - self.fade_to_volume) * elapsed_time / 1.5
                self.vlc_connection.send_message(f'volume {current_fade_volume}')
        self.vlc_connection.send_message(f'volume {self.fade_to_volume}')

    def fade_in_music_run(self):
        start_fade_time = time.clock()
        current_time = start_fade_time
        while current_time - start_fade_time < 1.5:
            time.sleep(0.01)
            current_time = time.clock()
            elapsed_time = current_time - start_fade_time
            if elapsed_time >= 1.5:
                elapsed_time = 1.5
            if self.current_volume > self.fade_to_volume:
                current_fade_volume = self.fade_to_volume + (self.current_volume - self.fade_to_volume) * elapsed_time / 1.5
                self.vlc_connection.send_message(f'volume {current_fade_volume}')
        self.vlc_connection.send_message(f'volume {self.current_volume}')


    def receive_vlc_messages(self, message):
        match = re.search(r'audio volume: \d\d*', message)
        if match and self.waiting_for_current_volume.is_set():
            parsed_message = match.group(0)
            volume = int(parsed_message.split(' ')[2])
            self.current_volume = volume
            self.waiting_for_current_volume.clear()


