import datetime
import os
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent
LOGS_ROOT = PROJECT_ROOT / "Logs"

class LogCatcher:
    def __init__(self, adb_serial, script_name):
        self.adb_serial = adb_serial
        self.script = script_name
        self.log_file = None
        self.logcat_proc = None
        self.logcat_flush = None
        self.project_root = Path(__file__).resolve().parent
        self.logs_root = self.project_root / "Logs"
        self.logs_root.mkdir(exist_ok=True)

    def create_log_directory(self):
        test_name = Path(self.script).stem
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        log_dir = self.logs_root / f"{test_name}_{timestamp}"
        log_dir.mkdir(parents=True, exist_ok=True)

        return str(log_dir)
    # timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        # script_name = self.script.split(".")[0]
        # folder_name = script_name + "_" + timestamp
        # print("[LogCatcher] Test logs folder: ", folder_name)
        # os.makedirs(folder_name, exist_ok=True)
        # log_folder_path = os.path.join(os.getcwd(), folder_name)
        # print("[LogCatcher] Absolute test log folder path: ", log_folder_path)
        # return log_folder_path

    def logcat_start(self, log_folder_path):
        log_path = os.path.join(log_folder_path, "logcat.txt")
        adb_command = ["adb", "-s", self.adb_serial, "logcat", "-v", "time"]
        logcat_buffer_erase = ["adb", "-s", self.adb_serial, "logcat", "-c"]
        print(f"[LogCatcher] Starting logcat for: {self.adb_serial} ", "-->", log_path)

        #try to erase logcat buffer to avoid old logs
        try:
            self.logcat_flush = subprocess.Popen(logcat_buffer_erase, stdout=self.log_file, stderr=subprocess.STDOUT)
        except Exception as e:
            raise RuntimeError(f"[LogCatcher] Error when trying to flush logcat buffer: {e}")

        # try to create a new file logcat.txt and write the logcat messages
        try:
            self.log_file = open(log_path, "ab")
            self.logcat_proc = subprocess.Popen(adb_command, stdout=self.log_file, stderr=subprocess.STDOUT)
            print(f"[LogCatcher] Logcat PID: {self.logcat_proc.pid}")
        except FileNotFoundError:
            self.log_file.close()
            raise RuntimeError(f"[LogCatcher] Unable to open {log_path}. Make sure you have installed ADB")
        except Exception as e:
            raise RuntimeError(f"[LogCatcher] Unable to run logcat. Error details: {e}")
        return self.logcat_proc, self.log_file

    def logcat_stop(self):
        print(f"[LogCatcher] Stopping logcat for {self.adb_serial}...")
        #check if logcat process exists at all
        if self.logcat_proc:
            try:
                #try to terminate the process with timeout=3 seconds
                self.logcat_proc.terminate()
                self.logcat_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                #if process is stuck or did not terminate for other reason -> force to kill
                print("[LogCatcher] Unable to terminate logcat process, killing...")
                self.logcat_proc.kill()
            except Exception as e:
                print(f"[LogCatcher] Error when trying to kill logcat process: {e}")
        else:
            print("[LogCatcher] Logcat process do not exist!")

        #check if logcat file is open
        if self.log_file:
            #try to close the file
            try:
                self.log_file.close()
            except Exception as e:
                print(f"[LogCatcher] Error when trying to close logcat file: {e}")

        print("[LogCatcher] Logcat process stopped")

