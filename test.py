import tkinter as tk
import socket
import subprocess
import threading
import json


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', 0))
print(socket.gethostname())
print(socket.gethostbyname(socket.gethostname()))
sock.close()
