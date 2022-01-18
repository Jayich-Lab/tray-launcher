from os import path, kill
from win32gui import IsWindowEnabled, IsWindowVisible
from win32gui import EnumWindows, ShowWindow, SetWindowPos
from win32process import GetWindowThreadProcessId, GetExitCodeProcess
from time import localtime, time
from pathlib import Path
from subprocess import Popen, PIPE, run, CREATE_NO_WINDOW
from signal import SIGTERM
from win32con import SW_RESTORE, HWND_NOTOPMOST, HWND_TOPMOST
from win32con import SWP_NOMOVE, SWP_NOSIZE, SWP_SHOWWINDOW

from PyQt5.QtCore import QObject

class ChildScriptManager(QObject):
    # key: int, value: ChildScript
    currently_running_ChildScripts = {}

    def __init__(self):
        super().__init__()

    def run_new(self, args):
        """Starts a new script.

        Args:
            args: (Path, int), the path to the script, 
                the timestamp of the ChildScript.
        """
        c = ChildScript(str(args[0]))
        c.start_script()
        self.currently_running_ChildScripts[args[1]] = c
        # print(self.currently_running_ChildScripts)

    def show(self, args):
        """Brings windows associated with a script to the foreground.

        Args:
            args: (Path, int), the path to the script, 
                the timestamp of the ChildScript.
        """
        self.currently_running_ChildScripts[args[1]].update_current_PIDs()
        self.bring_to_front(self.currently_running_ChildScripts[args[1]].current_PIDs)

    def terminate(self, timestamp):
        """Terminates the script started at the time specified 
            by the argument timestamp.

        Args:
            args: int, the timestamp of the ChildScript.
        """
        self.currently_running_ChildScripts[timestamp].terminate_script()
        del self.currently_running_ChildScripts[timestamp]

    def get_hwnds_for_PID(self, pid):
        """Get WINDOW handles for windows associated with the given PID.

        Args:
            pid: int, the PID whose window handles are to be found.
        """
        def callback(hwnd, hwnds):
            if IsWindowVisible(hwnd) and IsWindowEnabled(hwnd):
                _, found_pid = GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    hwnds.append(hwnd)
            return True
        hwnds = []
        EnumWindows(callback, hwnds)
        return hwnds

    def bring_to_front(self, pids):
        """Brings the windows of processes with the given pids to the foreground.

        Arg: 
            pids: list of int, PIDs of the processes whose windows are 
                to be brought to the foreground.
        """
        for pid in pids:
            for window_handle in self.get_hwnds_for_PID(pid):
                ShowWindow(window_handle, SW_RESTORE)
                SetWindowPos(window_handle, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE + SWP_NOSIZE)
                SetWindowPos(window_handle, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE + SWP_NOSIZE)
                SetWindowPos(window_handle, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_SHOWWINDOW 
                    + SWP_NOMOVE + SWP_NOSIZE)


class ChildScript():  
    ENCODING = 'utf-8'

    script_path_str = ""
    outputs_file = None

    childScript = None
    childScript_PID = -1
    childScript_PID_window_PID = -1

    current_PIDs = []

    def __init__(self, script_path_str):
        self.script_path_str = script_path_str

        self.USER_HOME = Path.home() / "tray_launcher"
        self.LOGS = self.USER_HOME / "logs"

    def start_script(self):
        script_path = Path(self.script_path_str)

        t = localtime(time())

        try:
            log_directory = self.LOGS / (str(t.tm_year) + "_" + str(t.tm_mon) + "_" + str(t.tm_mday))
            log_directory.mkdir(parents = True, exist_ok = True)
        except Exception as err:
            print(err + ": Failed to create new directory for outputs")
            raise

        self.log_path = log_directory / "{}-{}_{}_{}.log".format(script_path.stem, t.tm_hour, t.tm_min, t.tm_sec)

        try:
            self.outputs_file = open(self.log_path, 'a')  
        except Exception as err:
            print(err + ": Failed to open/create a file for outputs")
            raise

        self.childScript = Popen(self.script_path_str, encoding = self.ENCODING, stdout = self.outputs_file, stderr = self.outputs_file, creationflags=CREATE_NO_WINDOW)
        
        self.childScript_PID = self.childScript.pid
        print("childScript_PID: " + str(self.childScript_PID))

    def terminate_script(self):
        self.update_current_PIDs()
        try:
            for pid in self.current_PIDs:
                run(['taskkill', '/F', '/T', '/PID', str(pid)])
        except Exception:
            print("Error when terminating child processes.")

        try:
            self.outputs_file.close()
            kill(self.childScript_PID, SIGTERM)
        except OSError:
            print("The Popen process is not running")
            return

    def is_active(self):
        """Checks if there is any subprocess still running."""
        self.update_current_PIDs()
        # print(self.current_PIDs)
        # print(self.childScript.poll())

        if(self.current_PIDs):
            return True
        elif(self.childScript.poll() == None):
            return True

        return False

    def update_current_PIDs(self):
        self.current_PIDs = []
        wmic_ = run("wmic process where (ParentProcessId={}) get ProcessId".format(str(self.childScript_PID)), encoding = self.ENCODING, stdout = PIPE, shell = True)
        for line in wmic_.stdout.split("\n"):
            if  (line != "" and line.split(" ")[0] != "ProcessId"):
                self.current_PIDs.append(int(line))