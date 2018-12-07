import threading
import tkinter as tk
import socket
from tkinter import messagebox

root = tk.Tk()

tk.Label(root, text='Enter IP:').pack()
ip_entry = tk.Entry(root)
ip_entry.pack()
tk.Label(root, text='Enter IP:').pack()
port_entry = tk.Entry(root)
port_entry.pack()

sock = None
def connect():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = int(port_entry.get())
    sock.connect((ip_entry.get(), port))
    messagebox.showinfo('Connection Esablished', 'Connected to Timer')

tk.Button(root, text='Connect', command=connect).pack()

communication_with_server_lock = threading.Lock()
def send_message(message):
    communication_with_server_lock.acquire()
    if sock:
        sock.sendall(message.encode())
        response = sock.recv(1024)
        print(response)
    communication_with_server_lock.release()

tk.Button(root, text='Pause Media', command=lambda: send_message('pause_media\n')).pack()
tk.Button(root, text='Pause Timer', command=lambda: send_message('pause_timer\n')).pack()
tk.Button(root, text='Next Period', command=lambda: send_message('next_period\n')).pack()
tk.Button(root, text='Previous Period', command=lambda: send_message('previous_period\n')).pack()
tk.Button(root, text='Add 10 Seconds', command=lambda: send_message('add_10\n')).pack()
tk.Button(root, text='Add 30 Seconds', command=lambda: send_message('add_30\n')).pack()
tk.Button(root, text='Remove 10 Seconds', command=lambda: send_message('remove_10\n')).pack()
tk.Button(root, text='Remove 30 Seconds', command=lambda: send_message('remove_30\n')).pack()


root.mainloop()