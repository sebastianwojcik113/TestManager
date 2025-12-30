import subprocess
import re
import time

import iperf3_fixed as iperf3

IPERF_PATH = "/data/local/tmp/iperf3.9"
IPERF_PORT = "5201"
SERVER_ADDRESS = None

class IperfServerError(RuntimeError):
    pass

class IperfManager:
    DEFAULTS = {
        "Duration": 5,
        "Protocol": "TCP",
        "Bandwidth": 0,
        "Streams": 1,
        "Direction": "DL",
        "Port": 5201,
        "Expected_bitrate": 0
    }

    def __init__(self, params: dict):
        self.params = self.DEFAULTS.copy()
        self.params.update(params)
        self.server_ip = None
        self.server_proc = None


    def get_phone_ip(self):
        out = subprocess.check_output(
            ["adb", "shell", "ip", "route"],
            text=True
        )
        # regex to extract "src 192.168.1.123"
        match = re.search(r'src (\d+\.\d+\.\d+\.\d+)', out)
        if not match:
            raise RuntimeError("[ERROR] Unable to fetch DUT IP address")
        return match.group(1)

    def start_iperf_server(self):
        devices = subprocess.check_output(["adb", "devices"], text=True)
        if "\tdevice" not in devices:
            raise IperfServerError("[ERROR] No ADB devices found")

        rc = subprocess.run(
            ["adb", "shell", f"test -x {IPERF_PATH}"],
            stdout=subprocess.DEVNULL
        ).returncode

        if rc != 0:
            raise IperfServerError(f"No Iperf binary found: {IPERF_PATH}")

        proc = subprocess.Popen(
            ["adb", "shell", IPERF_PATH, "-s"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(1)

        ps = subprocess.check_output(
            ["adb", "shell", "pidof", "iperf3.9"],
            text=True
        ).strip()

        if not ps:
            stdout, stderr = proc.communicate(timeout=1)
            raise IperfServerError(
                "Iperf server did not started\n"
                f"stdout: {stdout}\n"
                f"stderr: {stderr}"
            )

        print("[OK] Iperf server started.")
        return proc

    def run_iperf_traffic(self):
        self.server_ip = self.get_phone_ip()
        self.start_iperf_server()

        try:
            client = iperf3.Client()
            client.server_hostname = self.server_ip
            client.port = self.params["Port"]
            client.duration = self.params["Duration"]
            client.num_streams = self.params["Streams"]
            client.json_output = True
            client.verbose = False

            # Protocol
            if self.params["Protocol"].upper() == "UDP":
                client.protocol = "udp"
            if self.params["Duration"] > 0:
                client.duration = self.params["Duration"]
            # Direction
            if self.params["Direction"].upper() == "UL":
                client.reverse = True
            elif self.params["Direction"].upper() == "DL":
                client.reverse = False
            if self.params["Bandwidth"] > 0:
                client.bandwidth = int(self.params["Bandwidth"])


            print(f"[INFO] Starting iperf traffic → {self.server_ip}")
            result = client.run()

            if result is None:
                raise IperfServerError("iperf returned no result")

            if result.error:
                raise IperfServerError(result.error)

            return self.print_results(result)



        finally:
            self.stop_iperf_server()


    # def print_results(self, result):
    #     print('')
    #     print('Test completed:')
    #     print('Started at           {0}'.format(result.time))
    #     print(f'Transferred data    {round(result.received_bytes/1e6, 2)} MB')
    #     print(f'Transferred data    {round(result.sent_bytes / 1e6, 2)} MB')
    #     print(f'AVg bitrate:        {round(result.received_Mbps, 2)} Mbps')

    def print_results(self, result):
        print("")
        print("Test completed:")
        print(f"Started at           {result.time}")

        measured = self._get_measured_bitrate(result)

        if result.protocol == "TCP":
            print(f"Transferred data     {round(result.received_bytes / 1e6, 2)} MB")

        print(f"Avg bitrate          {measured:.2f} Mbps")

        passed = self._check_expected_bitrate(measured)

        return {
            "Measured_Mbps": round(measured, 2),
            "Expected_Mbps": self.params["Expected_bitrate"],
            "Result": "PASS" if passed else "FAIL"
        }

    def _get_measured_bitrate(self, result):
        # Mbps
        if result.protocol == "TCP":
            if self.params["Direction"].upper() == "DL":
                return result.received_Mbps
            else:
                return result.sent_Mbps
        else:  # UDP
            return result.Mbps

    def _check_expected_bitrate(self, measured_mbps):
        expected = self.params["Expected_bitrate"]

        if expected <= 0:
            print("[INFO] Expected bitrate not defined – skipping check")
            return True

        if measured_mbps >= expected:
            print(
                f"[PASS] Bitrate OK: {measured_mbps:.2f} Mbps "
                f"(expected ≥ {expected} Mbps)"
            )
            return True
        else:
            print(
                f"[FAIL] Bitrate TOO LOW: {measured_mbps:.2f} Mbps "
                f"(expected ≥ {expected} Mbps)"
            )
            return False

    def stop_iperf_server(self):
        subprocess.run(
            ["adb", "shell", "pkill", "-f", "iperf3.9"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("[OK] Iperf server stopped.")


if __name__ == "__main__":
    TEST= {
        "Duration": 4,
        "Protocol": "TCP",
        "Bandwidth": 0,
        "Streams": 1,
        "Direction": "DL",
        "Port": 5201,
        "Expected_bitrate": 50
    }

    iperf_manager = IperfManager(TEST)
    iperf_manager.run_iperf_traffic()