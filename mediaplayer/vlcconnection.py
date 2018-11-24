import tkinter as tk
import socket
import subprocess
import threading
import json


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

        self.vlc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.vlc_sock.connect(('localhost',self.port))

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
        self.dispatch_thread_lock.acquire()
        if self.vlc_sock:
            self.vlc_sock.close()
            self.vlc_sock = None
            self.done_dispatching_messages.set()
        self.dispatch_thread_lock.release()




if __name__=='__main__':
    import tkinter as tk
    root = tk.Tk()

    def print_vlc_connection_message(message):
        print(message)

    vlc_connection = VLCConnection(r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe", print_vlc_connection_message)

    message_entry = tk.Entry(root)
    message_entry.pack()
    tk.Button(root, text='Send', command=lambda: vlc_connection.send_message(message_entry.get())).pack()

    root.mainloop()


