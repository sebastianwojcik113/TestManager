import json
from time import sleep

import ConnectionHandler
from ApManager import ApManager


class TestManager:
    def __init__(self, apconfig, ap_params=None):
        self.connection = ConnectionHandler.ConnectionHandler()
        self.ap_manager = None
        self.test_result = "NOT RUN"
        self.apconfig = apconfig #dict

    def load_commands_from_file(self, filename):
        try:
            with open(filename) as test_scenario_json:
                print(f"[INFO] File {filename} loaded. Proceeding with test sequence...")
                commands = json.load(test_scenario_json)
                test_scenario_json.close()
                return commands
        except OSError:
            test_scenario_json.close()
            print(f"[ERROR] File {filename} not found!")
        except ValueError:
            test_scenario_json.close()
            print(f"[ERROR] File {filename} is broken. Please check if file follows the JSON format!")

    def run_test_sequence(self, commands):
        self.connection.connect()
        response = None
        for i, command in enumerate(commands, start=1):
            # command_json = json.load(command)
            command_id = i
            command["Command_ID"] = command_id
            command_type = command.get("Command")
            timeout = command.get("Timeout", 10)

            # Run AP related commands locally, do not send to TestRunner
            if command_type == "AP_SETUP":
                self.ap_manager = ApManager(self.apconfig["IP"], self.apconfig["USER"], self.apconfig["PWD"])
                try:
                    self.ap_manager.setup_ap_basic(command)
                    print(f"[INFO] Command \"AP_SETUP\" sent to AP")
                    response = {"Result": "COMPLETE", "Command_ID": command_id}
                except Exception as e:
                    response = {"Result": "ERROR", "Command_ID": command_id}
                    print(f"[ERROR] AP setup process failed, reason: {e}")

            elif command_type == "AP_SWITCH_RADIO":
                self.ap_manager = ApManager(self.apconfig["IP"], self.apconfig["USER"], self.apconfig["PWD"])
                try:
                    self.ap_manager.switch_ap_radio(command)
                    print(f"[INFO] Command \"AP_SWITCH_RADIO\" sent top AP")
                    response = {"Result": "COMPLETE", "Command_ID": command_id}
                except Exception as e:
                    response = {"Result": "ERROR", "Command_ID": command_id}
                    print(f"[ERROR] AP switch radio failed, reason: {e}")
            # handle Delay command - just wait for desired time
            elif command_type == "DELAY":
                print(f"Start of delay timer, waiting for {timeout} seconds")
                sleep(timeout)

            else:
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

#simple main class for testing purpose
# if __name__ == '__main__':
#     ap = """
#         {
#       "IP": "192.168.1.9",
#       "USER": "admin",
#       "PWD": "PCVtest123$"
#     }
#     """
#     params = """{
#         "Command": "AP_SETUP",
#         "SSID": "Test_network",
#         "BAND": "6G",
#         "CHANNEL": "36",
#         "MODE": "ac",
#         "WIDTH": "40",
#         "SECURITY": "open",
#         "PWD": "testing123"
#         }"""
#     ap_params = json.loads(params)
#     ap_config = json.loads(ap)
#     object = TestManager(ap_config, ap_params)
#     commands = object.load_commands_from_file("Test_scripts/AP_setup.json")
#     object.run_test_sequence(commands)