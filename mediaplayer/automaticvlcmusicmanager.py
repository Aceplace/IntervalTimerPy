import re
import threading
import time

from mediaplayer.vlcmusicmanager import VLCMusicManager


class AutomaticVLCMusicManager(VLCMusicManager):
    def __init__(self, vlc_connection, get_song_callback):
        VLCMusicManager.__init__(self, vlc_connection)
        self.get_song_callback = get_song_callback
        threading.Thread(target=self.check_for_adding_song, daemon=True).start()


    def check_for_adding_song(self):
        while True:
            time.sleep(1.5)
            self.send_vlc_message('status')


    def receive_vlc_messages(self, message):
        VLCMusicManager.receive_vlc_messages(self, message)
        match = re.search(r' stop state: 5 ', message)
        if match and self.get_song_callback:
            new_song_path = self.get_song_callback()

            if new_song_path:
                self.send_vlc_message(f'add {new_song_path}')



