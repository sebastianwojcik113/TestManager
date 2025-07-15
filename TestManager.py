from time import sleep

import ConnectionHandler


class TestManager:
    def __init__(self):
        self.connection = ConnectionHandler.ConnectionHandler()
        self.test_result = "NOT RUN"

    def run_test_sequence(self, commands):
        #TODO zaimplementować klasę pobierania sekwencji komend z pliku XML/JSON? 
        try:
            self.connection.connect()
            all_passed = True



            for command in commands:
                self.connection.send_command(command)
                response = self.connection.receive_response(timeout=5)

                if response is None or "ERROR" in response.upper():
                    print(f"[Fail] Step '{command}' failed or no response")
                    all_passed = False
                    break
                else:
                    print(f"[OK] Step '{command}' confirmed")
                sleep(5)

            self.test_result = "PASS" if all_passed else "FAIL"
        finally:
            self.connection.close()
            print(f"\n[TestManager]: Final test result: {self.test_result}")