import argparse

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

    #Add checking if ADB serial is available
    #Add checking if AP is reachable - ping test

    #Enable test logs collection
    logCatcher = LogCatcher(dut["ADB_SERIAL"], script)
    logCatcher.logcat_start(logCatcher.create_log_directory())


    # Check port forwarding to communicate with DUT
    do_handler = DeviceOwnerHandler(host_port=HOST_PORT, device_port=DEVICE_PORT, expected_owner=EXPECTED_OWNER, adb_serial=dut["ADB_SERIAL"])
    if not do_handler.check_device_availability():
        print(f"[ERROR] Device not available. Stopping the run...")
        exit(1)
    do_handler.forward_port(HOST_PORT,DEVICE_PORT)
    if do_handler.check_device_owner(EXPECTED_OWNER):
        # Remove current Device Owner
        do_handler.remove_device_owner(EXPECTED_OWNER)
    # Install Test Runner apk
    do_handler.install_TR_apk()
    do_handler.set_device_owner(EXPECTED_OWNER)
    do_handler.run_TR_apk()


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

    #Remove Device Owner permissions
    do_handler.remove_device_owner(EXPECTED_OWNER)
    #Stop collecting the logs
    logCatcher.logcat_stop()

