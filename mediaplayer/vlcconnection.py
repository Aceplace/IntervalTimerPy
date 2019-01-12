import tkinter as tk
import socket
import subprocess
import threading
import json
import time


class VLCConnection:
    def __init__(self, vlc_path, vlc_message_callback=None):
        self.vlc_message_callback = vlc_message_callback
        #Find an open port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost',0))
        self.port = sock.getsockname()[1]
        sock.close()

        #open vlc at that port and set up communication to vlc and from it
        self.vlc_subprocess = subprocess.Popen([vlc_path, '--intf', 'qt', '--extraintf', 'rc', '--rc-host', f'localhost:{self.port}'])

        # Connect to vlc. Have to try multiple times because we won't successfully connect to vlc
        # until it is bound to the port, which could take a couple seconds.
        connected_to_vlc = False
        connection_attempts = 0
        while not connected_to_vlc:
            try:
                self.vlc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.vlc_sock.connect(('localhost',self.port))
                connected_to_vlc = True
            except ConnectionRefusedError:
                connection_attempts += 1
                if connection_attempts >= 50:
                    raise ConnectionRefusedError
                time.sleep(0.1)

        receive_and_dispatch_messages_thread = threading.Thread(target=self.receive_and_dispatch_messages_from_vlc, daemon=True)
        self.done_dispatching_messages = threading.Event()
        receive_and_dispatch_messages_thread.start()
        self.dispatch_thread_lock = threading.Lock()

    def send_message(self, message):
        if message[-1] != '\n':
            message += '\n'
        if self.vlc_sock:
            try:
                self.vlc_sock.sendall(message.encode())
            except Exception:
                self.close_connection()

    def receive_and_dispatch_messages_from_vlc(self):
        while not self.done_dispatching_messages.is_set():
            try:
                message = self.vlc_sock.recv(1024)
                if self.vlc_message_callback:
                    self.vlc_message_callback(message.decode())
            except Exception:
                self.close_connection()


    def close_connection(self):
        self.dispatch_thread_lock.acquire() #two possible threads may access this so neccessitating the lock
        if self.vlc_sock:
            self.vlc_sock.close()
            self.vlc_sock = None
            self.done_dispatching_messages.set()
        self.dispatch_thread_lock.release()



