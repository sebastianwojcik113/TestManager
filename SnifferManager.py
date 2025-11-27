import subprocess
import os
import signal
from datetime import datetime


class SnifferManager:
    def __init__(self, interface: str, channel: int, width: int = 20, output_dir="/tmp"):
        """
        :param interface: nazwa interfejsu sniffera (np. wlan1)
        :param channel: kanał pracy sniffera (np. 6, 36, 149)
        :param width: szerokość kanału w MHz (20/40/80/160)
        :param output_dir: katalog, gdzie będą zapisywane pliki .pcap
        """
        self.interface = interface
        self.channel = channel
        self.width = width
        self.output_dir = output_dir
        self.capture_process = None
        self.capture_file = None

        # Utwórz folder zapisu jeśli nie istnieje
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

    # -------------------------
    # 🛠 KONFIGURACJA KARTY
    # -------------------------
    def sniffer_configure(self):
        print(f"[INFO] Konfiguruję interfejs {self.interface} w tryb monitor...")

        self._run_cmd(f"sudo ifconfig {self.interface} down")
        self._run_cmd(f"sudo iw dev {self.interface} set type monitor")
        self._run_cmd(f"sudo iw dev {self.interface} set channel {self.channel} HT{self.width}")
        self._run_cmd(f"sudo ifconfig {self.interface} up")

        print(f"[OK] Sniffer skonfigurowany ({self.interface}, kanał {self.channel}, {self.width} MHz)")

    # -------------------------
    # ▶️ START SNIFFERA (TSHARK)
    # -------------------------
    def sniffer_start(self, file_prefix="capture"):
        """
        Uruchamia TShark i zapisuje dane do pliku .pcap
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.capture_file = f"{self.output_dir}/{file_prefix}_{self.interface}_{timestamp}.pcap"

        print(f"[INFO] Start sniffera na {self.interface} -> {self.capture_file}")

        cmd = [
            "sudo", "tshark",
            "-i", self.interface,
            "-I",             # włącz monitor mode sniffing (jeśli obsługiwany)
            "-w", self.capture_file,
            "-b", "duration:0"  # brak rotacji plików
        ]

        # uruchom jako proces background
        self.capture_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"[OK] Sniffer wystartował (PID: {self.capture_process.pid})")

    # -------------------------
    # ⏹ STOP SNIFFERA
    # -------------------------
    def sniffer_stop(self):
        if self.capture_process:
            print(f"[INFO] Zatrzymuję sniffera (PID: {self.capture_process.pid})...")
            self.capture_process.send_signal(signal.SIGINT)
            self.capture_process.wait()
            print(f"[OK] Zakończono! Plik zapisany: {self.capture_file}")
            self.capture_process = None
        else:
            print("[WARN] Sniffer nie był aktywny!")

    # -------------------------
    # 🔍 SPRAWDZENIE TRYBU MONITOR
    # -------------------------
    def check_monitor_mode(self) -> bool:
        output = self._run_cmd(f"iw dev | grep {self.interface} -A 5", output=True)
        is_monitor = "type monitor" in output
        print(f"[INFO] Monitor mode ({self.interface}) = {is_monitor}")
        return is_monitor

    # -------------------------
    # 🧰 Helper do komend
    # -------------------------
    def _run_cmd(self, cmd, output=False):
        try:
            if output:
                return subprocess.check_output(cmd, shell=True, text=True)
            subprocess.run(cmd, shell=True, check=True)
        except Exception as e:
            print(f"[ERROR] Problem wykonując '{cmd}': {e}")
            return ""


# -------------------------
# 👉 Przykład użycia
# -------------------------
if __name__ == "__main__":
    sniffer = SnifferManager(interface="wlan1", channel=36, width=80, output_dir="/tmp/sniffs")
    sniffer.sniffer_configure()
    sniffer.check_monitor_mode()
    sniffer.sniffer_start()
    # ... później np.: sniffer.sniffer_stop()
