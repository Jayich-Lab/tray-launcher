import logging
import os
import signal
import subprocess
import time as _t
from pathlib import Path

import psutil as _ps


class ChildScript:
    ENCODING = "utf-8"

    def __init__(self, pid, create_time, script_path, logging_log):
        """Create a ChildScript instance.

        This instance is used in reattaching processes when the tray launcher restarts.

        Args:
            pid: int, process id
            create_time: float, epoch time at the process' beginning
            script_path: Path, path to the script in the .tray_launcher folder
            logging_log: Path, path to the log of the tray launcher itself
        """

        logging.basicConfig(
            filename=logging_log,
            level=logging.INFO,
            format="%(asctime)s %(message)s",
        )

        self.script_path_str = str(script_path)
        self.script_path = script_path
        self.child_script = None
        self.child_script_PID = pid
        self.current_PIDs = []
        self.create_time = create_time

        if self.create_time != -1:
            self.access_file(_t.localtime(self.create_time))

    def access_file(self, t):
        """Use the creation time of the process to open its log file."""
        log_file = self.get_log_path()

        try:
            log_directory = log_file / (
                str(t.tm_year) + "_" + str(t.tm_mon).zfill(2) + "_" + str(t.tm_mday).zfill(2)
            )

            log_directory.mkdir(parents=True, exist_ok=True)
        except Exception as err:
            logging.error(err + ": Failed to create new directory for ChildScript outputs.")
            raise

        self.log_path = log_directory / "{}-{}_{}_{}.log".format(
            self.script_path.stem,
            str(t.tm_hour).zfill(2),
            str(t.tm_min).zfill(2),
            str(t.tm_sec).zfill(2),
        )

        try:
            self.outputs_file = open(self.log_path, "a+")
        except Exception as err:
            logging.error(err + ": Failed to open a file for ChildScript outputs.")
            raise

    def start_script(self):
        """Uses subprocess.Popen() to start the .bat file."""
        self.access_file(_t.localtime(_t.time()))

        self.child_script = subprocess.Popen(
            '"' + self.script_path_str + '"',
            encoding=self.ENCODING,
            stdout=self.outputs_file,
            stderr=self.outputs_file,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        self.child_script_PID = self.child_script.pid

        p = _ps.Process(self.child_script_PID)
        self.create_time = p.create_time()

    def terminate_script(self):
        self.update_current_PIDs()
        try:
            for pid in self.current_PIDs:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)])
        except Exception:
            logging.error(
                "Child Script PID: "
                + str(self.child_script_PID)
                + ": Error when terminating child processes."
            )

        try:
            self.outputs_file.close()
            os.kill(self.child_script_PID, signal.SIGTERM)
        except OSError:
            logging.error(
                "Child Script PID: "
                + str(self.child_script_PID)
                + ": The Popen process is not running."
            )
            return

    def get_log_path(self):
        user_home = Path.home() / ".tray_launcher"
        log_file = user_home / "logs"
        return log_file

    def is_active(self):
        """Checks if there is any subprocess still running."""
        self.update_current_PIDs()

        if self.child_script is not None and self.child_script.poll() is None:
            return True
        elif self.current_PIDs:
            return True
        return False

    def update_current_PIDs(self):
        """Populate the self.current_PIDs array with pids of child processes."""
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
