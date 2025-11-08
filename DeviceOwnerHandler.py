import subprocess
import time


class DeviceOwnerHandler:

    def __init__(self, host_port, device_port, expected_owner, adb_serial=None):
        self.host_port = host_port
        self.device_port = device_port
        self.expected_owner = expected_owner
        self.adb_serial = adb_serial

    def _adb_command(self, *args):
        cmd = ["adb"]
        if self.adb_serial:
            cmd += ["-s", self.adb_serial]
        cmd += list(args)
        return cmd

    # Prepare command to forward TCP port
    def forward_port(self, host_port, device_port):
        cmd = self._adb_command("forward", f"tcp:{host_port}", f"tcp:{device_port}")
        subprocess.run(cmd, check=True)
        # Delay to ensure forward is established
        time.sleep(0.5)

    #TODO Dodac obslugę wyjatku kiedy DUT nie jest autoryzowany do USB debuggingu

    def check_device_owner(self, expected_owner):
        cmd = self._adb_command("shell", "dpm", "list-owners")
        result = subprocess.run(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                check=True)
        output = result.stdout.strip()
        if expected_owner in output:
            print("Device owner already set")
        else:
            print("App is not set as Device Owner. Setting DO...")
            self.set_device_owner()

    def set_device_owner(self):
        cmd = self._adb_command("shell", "dpm", "set-device-owner",
                                "com.example.testrunner/.MyDeviceAdminReceiver")
        subprocess.run(cmd, check=True)
        print("App set as Device Owner successfully")

    # Delay to be sure forward is done
    time.sleep(0.5)