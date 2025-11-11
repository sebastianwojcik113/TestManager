import argparse
import json
import os
from fileinput import filename

from ConfigReader import ConfigReader
from DeviceOwnerHandler import DeviceOwnerHandler
from LogCatcher import LogCatcher
from TestManager import TestManager

if __name__ == '__main__':
    #some constant variables
    HOST_PORT = 5557  # port on PC
    DEVICE_PORT = 5557  # port on DUT
    EXPECTED_OWNER = "com.example.testrunner/.MyDeviceAdminReceiver"

    #Parse arguments (test script, adb serial?)
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", "-s", required=True, type=str)
    parser.add_argument("--config", "-c", required=True, type=str)
    args = parser.parse_args()
    script = args.script
    print(f"Script file name: {script}")
    config = args.config
    print(f"Config file name: {config}")

    # Read the test bed configuration
    configReader = ConfigReader(config)
    configReader.read_config()
    apconfig = configReader.get("AP")
    dut = configReader.get("DUT")

    #Enable test logs collection
    logCatcher = LogCatcher(dut["ADB_SERIAL"], script)
    logCatcher.logcat_start(logCatcher.create_log_directory())


    # Check port forwarding to communicate with DUT
    do_handler = DeviceOwnerHandler(host_port=HOST_PORT, device_port=DEVICE_PORT, expected_owner=EXPECTED_OWNER, adb_serial=dut["ADB_SERIAL"])
    do_handler.forward_port(HOST_PORT,DEVICE_PORT)
    #Remove current Device Owner
    do_handler.remove_device_owner(EXPECTED_OWNER)
    # Check if DO is already set
    do_handler.check_device_owner("admin=" + EXPECTED_OWNER)

    #Run initial test sequence to prepare DUT for testing
    testManager = TestManager(apconfig)
    initial_commands = testManager.load_commands_from_file("./Initial_sequence.json")
    testManager.run_test_sequence(initial_commands)

    # Start main Test Manager work
    commands = testManager.load_commands_from_file(script)
    if commands != None:
        testManager.run_test_sequence(commands)
    else:
        print(f"Unable to read test sequnce from file: {script}")

    #Stop collecting the logs
    logCatcher.logcat_stop()

