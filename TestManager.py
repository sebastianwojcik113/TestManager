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
            command_id = command_json.get("Command_ID")
            timeout = command_json.get("Timeout", 10)

            self.connection.send_command(command)
            response = self.connection.receive_response(command_id, timeout)

            if response is None:
                print(f"[Error] No response for Command_ID={command_id}")
                self.test_result = "FAIL"
                break

            if response.get("Result") == "ERROR":
                print(f"[Error] Command_ID={command_id} failed: {response}")
                self.test_result = "FAIL"
                break

            # Continue only if result was COMPLETE
            print(f"[Info] Command_ID={command_id} completed successfully.")
            sleep(2)  # Adjust if needed

        else:
            # Executed only if loop completes without 'break'
            self.test_result = "PASS"

        print(f"[{self.test_result}] Test finished with result: {self.test_result}")
        self.connection.close()
