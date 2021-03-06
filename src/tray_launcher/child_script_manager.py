from PyQt5.QtCore import QObject
from win32con import (
    HWND_NOTOPMOST,
    HWND_TOPMOST,
    SW_RESTORE,
    SWP_NOMOVE,
    SWP_NOSIZE,
    SWP_SHOWWINDOW,
)
from win32gui import EnumWindows, IsWindowEnabled, IsWindowVisible, SetWindowPos, ShowWindow
from win32process import GetWindowThreadProcessId

from tray_launcher import child_script


class ChildScriptManager(QObject):
    def __init__(self):
        super().__init__()

        self.running_child_scripts = {}

    def start_new_script(self, args):
        """Starts a new script by creating a ChildScript object and
            invoking the subprocess.Popen().

        Args:
            args: tuple of Path and Path, the path to the script;
                the path to the log file for the TRAY LAUNCHER, not this process.
        """
        child = child_script.ChildScript(-1, -1.0, args[0], args[1])
        child.start_script()
        self.running_child_scripts[child.create_time] = child

    def show(self, args):
        """Brings windows associated with a script to the foreground.

        Args:
            args: ((Path, int), str), the path to the script,
                the timestamp of the ChildScript.
                Plus the path to the log file for the tray launcher.
        """
        self.running_child_scripts[args[0][1]].update_current_PIDs()
        self.bring_to_front(self.running_child_scripts[args[0][1]].current_PIDs)

    def terminate(self, timestamp):
        """Terminates the script started at the time specified
            by the argument timestamp. Plus the path to the log file for the tray launcher.

        Args:
            args: (int, str), the timestamp of the ChildScript.
        """
        self.running_child_scripts[timestamp[0]].terminate_script()
        del self.running_child_scripts[timestamp[0]]

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
                SetWindowPos(
                    window_handle,
                    HWND_NOTOPMOST,
                    0,
                    0,
                    0,
                    0,
                    SWP_SHOWWINDOW + SWP_NOMOVE + SWP_NOSIZE,
                )
