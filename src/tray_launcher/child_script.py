import os
import signal
import subprocess
import time as _t
from pathlib import Path


class ChildScript:
    ENCODING = "utf-8"

    def __init__(self, script_path_str):
        self.script_path_str = script_path_str
        self.script_path = Path(self.script_path_str)
        self.child_script = None
        self.child_script_PID = -1
        self.current_PIDs = []

    def start_script(self):
        t = _t.localtime(_t.time())

        log_file = self.get_log_path()

        try:
            log_directory = log_file / (
                str(t.tm_year) + "_" + str(t.tm_mon).zfill(2) + "_" + str(t.tm_mday).zfill(2)
            )
            log_directory.mkdir(parents=True, exist_ok=True)
        except Exception as err:
            print(err + ": Failed to create new directory for outputs")
            raise

        self.log_path = log_directory / "{}-{}_{}_{}.log".format(
            self.script_path.stem,
            str(t.tm_hour).zfill(2),
            str(t.tm_min).zfill(2),
            str(t.tm_sec).zfill(2),
        )

        try:
            self.outputs_file = open(self.log_path, "a")
        except Exception as err:
            print(err + ": Failed to open/create a file for outputs")
            raise

        self.child_script = subprocess.Popen(
            '"' + self.script_path_str + '"',
            encoding=self.ENCODING,
            stdout=self.outputs_file,
            stderr=self.outputs_file,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        self.child_script_PID = self.child_script.pid
        print("child_script_PID: " + str(self.child_script_PID))

    def terminate_script(self):
        self.update_current_PIDs()
        try:
            for pid in self.current_PIDs:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)])
        except Exception:
            print("Error when terminating child processes.")

        try:
            self.outputs_file.close()
            os.kill(self.child_script_PID, signal.SIGTERM)
        except OSError:
            print("The Popen process is not running")
            return

    def get_log_path(self):
        user_home = Path.home() / ".tray_launcher"
        log_file = user_home / "logs"
        return log_file

    def is_active(self):
        """Checks if there is any subprocess still running."""
        self.update_current_PIDs()

        if self.child_script.poll() is None:
            return True
        elif self.current_PIDs:
            return True
        return False

    def update_current_PIDs(self):
        self.current_PIDs = []
        wmic_ = subprocess.run(
            "wmic process where (ParentProcessId={}) get ProcessId".format(
                str(self.child_script_PID)
            ),
            encoding=self.ENCODING,
            stdout=subprocess.PIPE,
            shell=True,
        )
        for line in wmic_.stdout.split("\n"):
            if line != "" and line.split(" ")[0] != "ProcessId":
                self.current_PIDs.append(int(line))
