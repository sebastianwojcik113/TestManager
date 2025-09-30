import argparse
import json
import socket
import subprocess
import time
from time import sleep

import ConnectionHandler
from DeviceOwnerHandler import DeviceOwnerHandler
from TestManager import TestManager

if __name__ == '__main__':
    ADB_SERIAL = "emulator-5554"  #"R5CWB0XESCJ"
    HOST_PORT = 5557  # port on PC
    DEVICE_PORT = 5557  # port on DUT
    EXPECTED_OWNER = "admin=com.example.testrunner/.MyDeviceAdminReceiver"

    #Parse arguments (test script, adb serial?)
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", "-s", required=True, type=str)
    parser.add_argument("--adb_serial", "-a", required=True, type=str)
    args = parser.parse_args()
    script = args.script
    dut_serial = args.adb_serial

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
