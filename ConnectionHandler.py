import json
import socket
import time


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
        self.sock = socket.create_connection((self.host, self.port), timeout=10)
        self.sock_file = self.sock.makefile('r')  # dla readline()
        welcome = self.sock_file.readline()
        print(f"[TestRunner]: {welcome.strip()}")

    def send_command(self, cmd):
        print(f"[TestManager]: Sending command -> {cmd}")
        self.sock.sendall((cmd + '\n').encode())

    def receive_response(self, expected_command_id, timeout):
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.sock_file.readline()
            if not response:
                print("[Warning] Empty response (connection closed?)")
                return None

            response = response.strip()
            try:
                json_format_response = json.loads(response)
            except json.JSONDecodeError:
                print(f"[Warning] Received non-JSON response: {response}")
                continue

            if "Ack_ID" in json_format_response:
                if json_format_response["Ack_ID"] == expected_command_id:
                    print(f"[TestRunner] ACK matched: {json_format_response}")
                    return json_format_response
                else:
                    print(f"[TestRunner] Ignored ACK for other command: {json_format_response}")
                    continue
            else:
                print(f"[TestRunner] Other message: {json_format_response}")
                continue

        print(f"[Timeout] No ACK for Command_ID={expected_command_id} after {timeout}s")
        return None

    def close(self):
        print("[Info] Closing connection")
        if self.sock:
            self.sock.close()