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

    # Check port forwarding to communicate with DUT
    do_handler = DeviceOwnerHandler(host_port=HOST_PORT, device_port=DEVICE_PORT, expected_owner=EXPECTED_OWNER, adb_serial=ADB_SERIAL)
    do_handler.forward_port(HOST_PORT,DEVICE_PORT)
    # Check if DO is already set
    do_handler.check_device_owner(EXPECTED_OWNER)

    # Start main Test Manager work
    #TODO wydzielić pobieranie sekwencji komend do osobnej funkcji/klasy
    commands = [
        "{\"Command_ID\":1, \"Command\":\"ENABLE_WIFI\"}",
        "{\"Command_ID\":2, \"Command\":\"WIFI_ADD_NETWORK\", \"SSID\":\"AndroidWifi\", \"SECURITY_TYPE\":\"OPEN\"}",
        "{\"Command_ID\":2, \"Command\":\"WIFI_ADD_NETWORK\", \"SSID\":\"AndroidWifi_wrong\", \"SECURITY_TYPE\":\"WPA2\", \"PWD\":\"12345678\"}",
        "{\"Command_ID\":2, \"Command\":\"WIFI_CONNECT\", \"SSID\":\"AndroidWifi_wrong\"}",
        #"{\"Command_ID\":3, \"Command\":\"DISABLE_WIFI\"}",
        # "{\"Command_ID\":4, \"Command\":\"CLOSE_CONNECTION\"}"
    ]

    testManager = TestManager()
    testManager.run_test_sequence(commands)
