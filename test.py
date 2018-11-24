import tkinter as tk
import socket
import subprocess
import threading
import json


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', 0))
port = sock.getsockname()[1]
sock.close()

subprocess.Popen([r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe", '--intf', 'qt', '--extraintf', 'rc', '--rc-host', f'localhost:{port}'])
#subprocess.Popen([r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe", '--intf', 'qt', '--extraintf', 'rc'])


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost',port))

root = tk.Tk()
message_entry = tk.Entry(root)
message_entry.pack()

def send_message():
    message = str(message_entry.get()) + '\n'
    message = message.encode()
    try:
        sock.sendall(message)
    except ConnectionResetError:
        sock.close()


def listen_to_vlc():
    while True:
        message = sock.recv(1024)
        if not message:
            break
        else:
            parse_message(message.decode())
    print('done listening to vlc')

def parse_message(message):
    import re
    match = re.search(r'audio volume: \d\d*', message)
    if match:
        print('match' + match.group(0))
    else:
        print('no match: ' + message)

thread = threading.Thread(target=listen_to_vlc, daemon=True)
thread.start()

tk.Button(root, text='Send', command=send_message).pack()



root.mainloop()