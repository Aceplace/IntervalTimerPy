import socket
import threading

class TCPInterface:
    def __init__(self):
        self.interval_timer = None
        self.connected = False
        self.connection = None
        self.message_callback = None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('',0))
        self.host_ip = socket.gethostbyname(socket.gethostname())
        self.port = self.sock.getsockname()[1]
        self.sock.listen(1)

        threading.Thread(target=self.wait_for_connection, daemon=True).start()

    def wait_for_connection(self):
        connection, address = self.sock.accept()
        self.connected = True
        self.connection = connection
        threading.Thread(target=self.handle_messages, daemon=True).start()

    def handle_messages(self):
        try:
            while True:
                message = self.connection.recv(1024)
                if self.message_callback:
                    response = self.message_callback(message.decode())
                else:
                    response = 'No attached interval timer.'
                if response:
                    self.connection.sendall(response.encode())
                else:
                    self.connection.sendall('No response'.encode())
        except (ConnectionResetError, ConnectionAbortedError):
            self.connection.close()
        threading.Thread(target=self.wait_for_connection, daemon=True).start()


