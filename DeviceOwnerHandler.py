import subprocess
import time


class DeviceOwnerHandler:


    def __init__(self, host_port, device_port, expected_owner):
        self.host_port = host_port
        self.device_port = device_port
        self.expected_owner = expected_owner

    # Prepare command to forward TCP port
    def forward_port(self, host_port, device_port):
        subprocess.run(["adb", "forward",
                        f"tcp:{host_port}", f"tcp:{device_port}"],
                       check=True)

    def check_device_owner(self, expected_owner):
        # Check if TestRunner app already has Device Owner permissions
        do_check_result = subprocess.run(["adb", "shell", "dpm", "list-owners"],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         text=True,
                                         check=True)
        # Set DO if required
        do_check_output = do_check_result.stdout.strip()
        if expected_owner in do_check_output:
            print("Device owner already set")
        else:
            print("App is not set as Device Owner. Setting DO...")
            self.setDeviceOwner()

    def set_device_owner(self):
        subprocess.run(["adb", "shell", "dpm", "set-device-owner", "com.example.testrunner/.MyDeviceAdminReceiver"],
                       check=True)
        print("App set as Device Owner successfully")

    # Delay to be sure forward is done
    time.sleep(0.5)