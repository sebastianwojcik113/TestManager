import socket


class ConnectionHandler:
    HOST_PORT = 5557  # port na PC
    HOST = 'localhost'


    def __init__(self, host=HOST, port=HOST_PORT):
        self.host = host
        self.port = port
        self.sock = None
        self.sock_file = None

    def connect(self):
        print(f"[Info] Connecting to TestRunner at {self.host}:{self.port}")
        self.sock = socket.create_connection((self.host, self.port), timeout=5)
        self.sock_file = self.sock.makefile('r')  # dla readline()
        welcome = self.sock_file.readline()
        print(f"[TestRunner]: {welcome.strip()}")

    def send_command(self, cmd):
        print(f"[TestManager]: Sending command -> {cmd}")
        self.sock.sendall((cmd + '\n').encode())

    def receive_response(self, timeout=5):
        self.sock.settimeout(timeout)
        try:
            response = self.sock_file.readline()
            if response:
                print(f"[TestRunner]: {response.strip()}")
                return response.strip()
            else:
                print("[Warning] Empty response (connection closed?)")
                return None
        except socket.timeout:
            print("[Error] Timeout while waiting for response")
            return None

    def close(self):
        print("[Info] Closing connection")
        if self.sock:
            self.sock.close()