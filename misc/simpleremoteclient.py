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

def send_message(message):
    if sock:
        sock.sendall(message.encode())
        response = sock.recv(1024)
        print(response)

tk.Button(root, text='Pause Media', command=lambda: send_message('pause_media\n')).pack()
tk.Button(root, text='Pause Timer', command=lambda: send_message('pause_timer\n')).pack()


root.mainloop()