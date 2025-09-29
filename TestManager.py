import json
from time import sleep

import ConnectionHandler


class TestManager:
    def __init__(self):
        self.connection = ConnectionHandler.ConnectionHandler()
        self.test_result = "NOT RUN"

    def load_commands_from_file(self, filename):
        try:
            with open(filename) as test_scenario_json:
                print(f"File {filename} loaded. Proceeding with test sequence...")
                commands = json.load(test_scenario_json)
                return commands
        except OSError:
            print(f"[Error] File {filename} not found!")
        except ValueError:
            print(f"[Error] File {filename} is broken. Please check if file follows the JSON format!")

    def run_test_sequence(self, commands):
        #TODO zaimplementować klasę pobierania sekwencji komend z pliku XML/JSON? 
        self.connection.connect()
        for command in commands:
            # command_json = json.load(command)
            command_id = command.get("Command_ID")
            command_type = command.get("Command")
            timeout = command.get("Timeout", 10)

            self.connection.send_command(command)
            response = self.connection.receive_response(command_id, timeout)

            if response is None:
                print(f"[Error] No response for Command_ID={command_id} {command_type}")
                self.test_result = "FAIL"
                break

            if response.get("Result") == "ERROR":
                print(f"[Error] Command_ID={command_id} {command_type} failed: {response}")
                self.test_result = "FAIL"
                break

            # Continue only if result was COMPLETE
            print(f"[Completed] Command_ID={command_id} {command_type} completed successfully.")
            sleep(2)  # Adjust if needed

        else:
            # Executed only if loop completes without 'break'
            self.test_result = "PASS"

        print(f"[{self.test_result}] Test finished with result: {self.test_result}")
        self.connection.close()
