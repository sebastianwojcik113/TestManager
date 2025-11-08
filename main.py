import argparse
import os

from DeviceOwnerHandler import DeviceOwnerHandler
from LogCatcher import LogCatcher
from TestManager import TestManager

if __name__ == '__main__':
    #some constant variables
    HOST_PORT = 5557  # port on PC
    DEVICE_PORT = 5557  # port on DUT
    EXPECTED_OWNER = "admin=com.example.testrunner/.MyDeviceAdminReceiver"

    #Parse arguments (test script, adb serial?)
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", "-s", required=True, type=str)
    parser.add_argument("--adb_serial", "-a", required=True, type=str)
    args = parser.parse_args()
    script = args.script
    print(f"Script file name: {script}")
    dut_serial = args.adb_serial
    print(f"DUT ADB serial: {dut_serial}")

    #Enable test logs collection
    logCatcher = LogCatcher(dut_serial, script)
    logCatcher.logcat_start(logCatcher.create_log_directory())


    # Check port forwarding to communicate with DUT
    do_handler = DeviceOwnerHandler(host_port=HOST_PORT, device_port=DEVICE_PORT, expected_owner=EXPECTED_OWNER, adb_serial=dut_serial)
    do_handler.forward_port(HOST_PORT,DEVICE_PORT)
    # Check if DO is already set
    do_handler.check_device_owner(EXPECTED_OWNER)

    # Start main Test Manager work
    testManager = TestManager()
    commands = testManager.load_commands_from_file(script)
    if commands != None:
        testManager.run_test_sequence(commands)

    #Stop collecting the logs
    logCatcher.logcat_stop()