import os.path
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
    def check_device_availability(self):
        result = subprocess.run(["adb", "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout.strip().splitlines()
        #check if there are any devices detected (first list element is always "List of devices attached")
        if len(output) <= 1:
            print("[ERROR] No ADB devices found!")
            return False
        devices_list = []
        for device in output[1:]:
            if device.strip():
                devices_list.append(device.split())
        print(devices_list)
        target_device = []
        for device in devices_list:
            if device[0] == self.adb_serial:
                target_device.append(device)
                print(f"[INFO] ADB device {self.adb_serial} found on list")
        if not target_device:
            print(f"[ERROR] Target device {self.adb_serial} not found!")
            return False
        print(target_device)
        if target_device[0][1] != "device":
            print(f"[ERROR] Target device {self.adb_serial} offline or unauthorized!")
            return False
        else:
            print(f"[INFO] Target device found and ready for test")
            return True

    def install_TR_apk(self):
        apk_path = os.path.abspath("TestRunnerApk/app-debug.apk")
        print("[INFO] Attempting to install Test Runner apk")
        cmd = self._adb_command("install", "-r", "-t", apk_path)
        subprocess.run(cmd, check=True)
        print("[INFO] Test Runner apk installed successfully")

    def run_TR_apk(self):
        full_name = "com.example.testrunner/.MainActivity"
        cmd = self._adb_command("shell", "am", "start", "-n", full_name)
        print(f"[INFO] Launching app: {full_name}")
        subprocess.run(cmd, check=True)
        time.sleep(2)
        print("[OK] App launched.")

    def remove_device_owner(self, deviceOwner):
        cmd = self._adb_command("shell", "dpm", "remove-active-admin", deviceOwner)
        print("[INFO] Removing current Device Owner...")
        subprocess.run(cmd, check=True)

    def check_device_owner(self, expected_owner):
        listed_owner = "admin=" + expected_owner
        cmd = self._adb_command("shell", "dpm", "list-owners")
        result = subprocess.run(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                check=True)
        output = result.stdout.strip()
        if listed_owner in output:
            print(f"[OK] Device owner already set")
            return True
        else:
            print("[INFO] App is not set as Device Owner")
            return False
            # self.set_device_owner(expected_owner)

    def set_device_owner(self, device_owner):
        #skip if DO is already set
        if self.check_device_owner(device_owner):
            print("[INFO] Device Owner already set. Skipping..")
        cmd = self._adb_command("shell", "dpm", "set-device-owner",
                                device_owner)
        print("[INFO] Setting Device Owner...")
        subprocess.run(cmd, check=True)
        print("[OK] App set as Device Owner successfully")

    def install_iperf(self, iperf_files_path):
        iperf_binaries = os.path.abspath("Iperf_binary/*")
        iperf_path = "/data/local/tmp/"
        print("[INFO] Copying Iperf binary files to device storage")
        cmd_push = self._adb_command("push", iperf_binaries, iperf_path)
        subprocess.run(cmd_push, check=True)
        print("[INFO] Setting permissions for Iperf binary files")
        cmd_permissions = self._adb_command("shell", "chmod +x", iperf_path + "*")
        subprocess.run(cmd_permissions, check=True)
        print("[INFO] Execute permissions granted")

    # Delay to be sure forward is done
    time.sleep(0.5)

# # Simple main for testing purpose
# if __name__ == '__main__':
#     object = DeviceOwnerHandler("5557", "5557","com.example.testrunner/.MyDeviceAdminReceiver", "R5CWB0XESCJ")
#     # object.set_device_owner()
#     object.check_device_owner("com.example.testrunner/.MyDeviceAdminReceiver")
#     # object.remove_device_owner("com.example.testrunner/.MyDeviceAdminReceiver")
#     # object.set_device_owner()
#     # object.run_TR_apk()
#     # object.remove_device_owner("com.example.testrunner/.MyDeviceAdminReceiver")