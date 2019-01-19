import time
import re
import threading

class VLCMusicManager:
    def __init__(self, vlc_connection, fade_to_volume=50):
        self.vlc_connection = vlc_connection
        self.current_volume = 0
        self.fade_to_volume = fade_to_volume
        self.skip_fade = False
        self.restoring_current_volume = False
        self.waiting_for_current_volume = threading.Event()
        self.sending_vlc_message_lock = threading.Lock()


    def pause(self):
        self.send_vlc_message('pause')

    def vol_up(self):
        self.send_vlc_message('volup 1')

    def vol_down(self):
        self.send_vlc_message('voldown 1')

    def skip_song(self):
        self.vlc_connection.send_message('next')

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
            if not self.skip_fade and not self.waiting_for_current_volume.is_set() and self.current_volume > self.fade_to_volume:
                current_fade_volume = self.current_volume - (self.current_volume - self.fade_to_volume) * elapsed_time / 1.5
                self.send_vlc_message(f'volume {current_fade_volume}')
        if not self.skip_fade:
            self.send_vlc_message(f'volume {self.fade_to_volume}')


    def fade_in_music_run(self):
        start_fade_time = time.clock()
        current_time = start_fade_time
        while current_time - start_fade_time < 1.5:
            time.sleep(0.01)
            current_time = time.clock()
            elapsed_time = current_time - start_fade_time
            if elapsed_time >= 1.5:
                elapsed_time = 1.5
            if not self.skip_fade and self.current_volume > self.fade_to_volume:
                current_fade_volume = self.fade_to_volume + (self.current_volume - self.fade_to_volume) * elapsed_time / 1.5
                self.send_vlc_message(f'volume {current_fade_volume}')
        if not self.skip_fade and not self.restoring_current_volume:
            threading.Thread(target=self.restore_current_volume, daemon=True).start()


    # Have to continually attempt to restore volume because vlc won't set volume while in pause mode
    def restore_current_volume(self):
        self.restoring_current_volume = True
        while self.restoring_current_volume:
            self.send_vlc_message(f'volume {self.current_volume}')
            time.sleep(0.5)


    def send_vlc_message(self, message):
        self.sending_vlc_message_lock.acquire()
        self.vlc_connection.send_message(message)
        self.sending_vlc_message_lock.release()


    def receive_vlc_messages(self, message):
        match = re.search(r'audio volume: \d\d*', message)
        if match and self.restoring_current_volume:
            self.restoring_current_volume = False
        elif match and self.waiting_for_current_volume.is_set():
            parsed_message = match.group(0)
            volume = int(parsed_message.split(' ')[2])
            self.current_volume = volume
            self.skip_fade = False
            self.waiting_for_current_volume.clear()

        match = re.search(r"Type 'pause' to continue", message)
        if match and self.waiting_for_current_volume.is_set():
            self.skip_fade = True
            self.waiting_for_current_volume.clear()


