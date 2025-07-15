import socket
import subprocess
import time
from time import sleep

import ConnectionHandler
from DeviceOwnerHandler import DeviceOwnerHandler
from TestManager import TestManager

if __name__ == '__main__':
    HOST_PORT = 5557  # port on PC
    DEVICE_PORT = 5557  # port on DUT
    EXPECTED_OWNER = "admin=com.example.testrunner/.MyDeviceAdminReceiver"

    # Check port forwarding to communicate with DUT
    do_handler = DeviceOwnerHandler(host_port=HOST_PORT, device_port=DEVICE_PORT, expected_owner=EXPECTED_OWNER)
    do_handler.forward_port(HOST_PORT,DEVICE_PORT)
    # Check if DO is already set
    do_handler.check_device_owner(EXPECTED_OWNER)

    # Start main Test Manager work
    #TODO wydzielić pobieranie sekwencji komend do osobnej funkcji/klasy
    commands = [
        "{\"Command_ID\":1, \"Command\":\"ENABLE_WIFI\"}",
        "{\"Command_ID\":2, \"Command\":\"WIFI_ADD_NETWORK\", \"SSID\":\"AndroidWifi\", \"SECURITY_TYPE\":\"WPA2\", \"PWD\":\"12345678\"}",
        "{\"Command_ID\":3, \"Command\":\"DISABLE_WIFI\"}"
    ]

    testManager = TestManager()
    testManager.run_test_sequence(commands)
