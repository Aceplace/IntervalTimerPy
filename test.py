import tkinter as tk
import socket
import subprocess
import threading
import json

json_string = '{"2": null}'
print(json.loads(json_string))

p = subprocess.Popen([r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe", '--intf', 'qt', '--extraintf', 'rc', '--rc-host', 'localhost:50000'])
#p = subprocess.Popen([r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe", '--intf', 'qt', '--extraintf', 'rc'])


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost',50000))

root = tk.Tk()
message_entry = tk.Entry(root)
message_entry.pack()

def send_message():
    message = str(message_entry.get()) + '\n'
    message = message.encode()
    sock.sendall(message)


def listen_to_vlc():
    while True:
        message = sock.recv(1024)
        print(message)

thread = threading.Thread(target=listen_to_vlc)
thread.start()

tk.Button(root, text='Send', command=send_message).pack()



root.mainloop()