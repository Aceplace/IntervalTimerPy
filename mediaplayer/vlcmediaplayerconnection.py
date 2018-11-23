import tkinter as tk
import socket
import subprocess
import threading
import json


class VLCMediaPlayerConnection:
    def __init__(self, vlc_message_callback=None):
        self.vlc_message_callback = vlc_message_callback
        #Find an open port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost',0))
        self.port = sock.getsockname()[1]
        sock.close()

        #open vlc at that port and set up communication to vlc and from it
        subprocess.Popen([r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe", '--intf', 'qt', '--extraintf', 'rc', '--rc-host', f'localhost:{self.port}'])

        self.vlc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.vlc_sock.connect(('localhost',self.port))

        thread = threading.Thread(target=self.receive_and_dispatch_messages_from_vlc)
        self.thread_event = threading.Event()
        thread.start()

    def send_message_to_vlc(self, message):
        if message[-1] != '\n':
            message += '\n'
        self.vlc_sock.sendall(message.encode())

    def receive_and_dispatch_messages_from_vlc(self):
        while not self.thread_event.is_set():
            message = self.vlc_sock.recv(1024)
            if self.vlc_message_callback:
                self.vlc_message_callback(message.decode())


if __name__=='__main__':
    import tkinter as tk
    root = tk.Tk()

    def print_vlc_connection_message(message):
        print(message)

    vlc_connection = VLCMediaPlayerConnection(print_vlc_connection_message)

    message_entry = tk.Entry(root)
    message_entry.pack()
    tk.Button(root, text='Send', command=lambda: vlc_connection.send_message_to_vlc(message_entry.get())).pack()

    root.mainloop()


