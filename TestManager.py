import json
from time import sleep

import ConnectionHandler


class TestManager:
    def __init__(self):
        self.connection = ConnectionHandler.ConnectionHandler()
        self.test_result = "NOT RUN"

    def run_test_sequence(self, commands):
        #TODO zaimplementować klasę pobierania sekwencji komend z pliku XML/JSON? 
        self.connection.connect()
        for command in commands:
            command_json = json.loads(command)
            self.connection.send_command(command)
            self.connection.receive_response(command_json["Command_ID"], command_json["Timeout"])
