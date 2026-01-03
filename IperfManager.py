import json
import os
import subprocess
import re
import tempfile
import time

import iperf3

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

    def __init__(self, params: dict, log_folder_path: str):
        self.params = self.DEFAULTS.copy()
        self.params.update(params)
        self.server_ip = None
        self.server_proc = None
        self.log_folder_path = log_folder_path


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

    import json
    import tempfile
    import os
    import subprocess
    import threading

    def run_iperf_traffic(self):
        self.server_ip = self.get_phone_ip()
        self.start_iperf_server()

        json_path = os.path.join(self.log_folder_path, "Iperf_result.json")

        try:
            # 1️⃣ Budowa komendy iperf3
            cmd = [
                "iperf3",
                "-c", self.server_ip,
                "-p", str(self.params["Port"]),
                "-t", str(self.params["Duration"]),
                "--json",
                "--logfile", json_path
            ]

            # Protocol
            if self.params["Protocol"].upper() == "UDP":
                cmd.append("-u")
                if self.params["Bandwidth"] > 0:
                    cmd += ["-b", str(self.params["Bandwidth"]) + "M"]

            # Streams
            if self.params["Streams"] > 1:
                cmd += ["-P", str(self.params["Streams"])]

            # Direction
            if self.params["Direction"].upper() == "UL":
                cmd.append("-R")

            print(f"[INFO] Starting iperf traffic → {self.server_ip}")
            print("[INFO] Command:", " ".join(cmd))

            # 2️⃣ Start procesu
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # 3️⃣ LIVE PRINTY
            for line in proc.stdout:
                print(line, end="")

            proc.wait()

            if proc.returncode != 0:
                raise IperfServerError("iperf3 client exited with error")

            # 4️⃣ Parsowanie JSON
            if not os.path.exists(json_path) or os.path.getsize(json_path) == 0:
                raise IperfServerError("iperf did not generate JSON output")

            with open(json_path) as f:
                result = json.load(f)

            # 5️⃣ Czytelne podsumowanie
            return self.print_results_from_json(result)

        finally:
            self.stop_iperf_server()

    # def print_results(self, result):
    #     print('')
    #     print('Test completed:')
    #     print('Started at           {0}'.format(result.time))
    #     print(f'Transferred data    {round(result.received_bytes/1e6, 2)} MB')
    #     print(f'Transferred data    {round(result.sent_bytes / 1e6, 2)} MB')
    #     print(f'AVg bitrate:        {round(result.received_Mbps, 2)} Mbps')

    def print_results_from_json(self, data):
        print("\n" + "=" * 60)
        print(" IPERF TRAFFIC SUMMARY")
        print("=" * 60)

        proto = self.params["Protocol"].upper()
        direction = self.params["Direction"].upper()
        duration = self.params["Duration"]

        measured = self._get_measured_bitrate_from_json(data)
        result = self._check_expected_bitrate(measured)

        print(f"Protocol        : {proto}")
        print(f"Direction       : {direction}")
        print(f"Duration        : {duration} s")
        print(f"Streams         : {self.params['Streams']}")
        print("-" * 60)

        print(f"Average bitrate : {measured:.2f} Mbps")

        if proto == "TCP":
            print(f"Retransmissions : {data['end']['sum_sent'].get('retransmits', 'N/A')}")
        if proto == "UDP":
            print(f"Jitter : {data['end']['sum'].get('jitter_ms', 'N/A')}, ms")
            print(f"Transmitted packets : {data['end']['sum'].get('packets', 'N/A')}")
            print(f"Lost packets : {data['end']['sum'].get('lost_packets', 'N/A')} ({round(data['end']['sum'].get('lost_percent', 'N/A'), 2)}%)")

        if self.params["Expected_bitrate"] > 0:
            print(f"Expected bitrate: ≥ {self.params['Expected_bitrate']} Mbps")
            print(f"RESULT          : {result}")

        else:
            print("Expected bitrate: not defined")
            print("RESULT          : N/A")

        print("-" * 60)
        if result is True:
            print(f"[PASS] Bitrate OK: {measured:.2f} Mbps")
        elif result is False:
            print(f"[FAIL] Bitrate too LOW: {measured:.2f} Mbps")
        else:
            print("RESULT          : SKIPPED")

        print("=" * 60)

        return {
            "Measured_Mbps": round(measured, 2),
            "Expected_Mbps": self.params["Expected_bitrate"],
            "Result": result
        }


    def _get_measured_bitrate_from_json(self, data):
        if self.params["Protocol"].upper() == "TCP":
            if self.params["Direction"].upper() == "DL":
                return data["end"]["sum_received"]["bits_per_second"] / 1e6
            else:
                return data["end"]["sum_sent"]["bits_per_second"] / 1e6
        else:
            return data["end"]["sum"]["bits_per_second"] / 1e6

    def _check_expected_bitrate(self, measured_mbps):
        expected = self.params["Expected_bitrate"]

        if expected <= 0:
            return None  # brak checka

        return measured_mbps >= expected


    def stop_iperf_server(self):
        subprocess.run(
            ["adb", "shell", "pkill", "-f", "iperf3.9"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("[OK] Iperf server stopped.")


if __name__ == "__main__":
    TEST= {
        "Duration": 5,
        "Protocol": "UDP",
        "Bandwidth": 1200,
        "Streams": 1,
        "Direction": "DL",
        "Port": 5201,
        "Expected_bitrate": 500
    }

    iperf_manager = IperfManager(TEST, "//home/sebastian/WifiTester/TestManager/Test_scripts/IPERF_202601031810")
    iperf_manager.run_iperf_traffic()