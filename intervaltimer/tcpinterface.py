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
        print('TCP Connection Waiting for Connection...')
        connection, address = self.sock.accept()
        self.connected = True
        self.connection = connection
        print(f'TCP Connection Connected to {connection}')
        threading.Thread(target=self.handle_messages, daemon=True).start()

    def handle_messages(self):
        try:
            self.connection.settimeout(10)
            message = ''
            while True:
                print("TCP Connection Waiting for Message...")
                incoming_data = self.connection.recv(1024)
                print(f"TCP Connection Received Data: {incoming_data}")

                if not incoming_data:
                    break
                message += incoming_data.decode()

                while '\n' in message:
                    index_of_newline = message.find('\n')
                    message_to_send = message[0:index_of_newline]
                    if index_of_newline == len(message):
                        message = ''
                    else:
                        message = message[index_of_newline+1:]

                    print(f"TCP Message To Send: {message_to_send}")
                    print(f"TCP Message Remaining: {message}")

                    self.handle_message(message_to_send)

        except (ConnectionResetError, ConnectionAbortedError, socket.timeout):
            pass
        finally:
            print('Connection closed')
            self.connection.close()
            self.connected = False
            self.connection = None
        threading.Thread(target=self.wait_for_connection, daemon=True).start()

    def handle_message(self, message):
        if self.message_callback:
            response = self.message_callback(message)
        else:
            response = 'No attached interval timer.'

        if response:
            print(f"TCP Connection Sending Response: {response}")
            self.connection.sendall(response.encode())
        else:
            print(f"TCP Connection Sending Response: No response")
            self.connection.sendall('No response'.encode())



