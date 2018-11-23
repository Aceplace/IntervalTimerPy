import socket
import tkinter as tk
import subprocess

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost',0))




root = tk.Tk()

root.mainloop()