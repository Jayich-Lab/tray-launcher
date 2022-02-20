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
    # key: timestamp
    # value: ChildScript
    currently_running_ChildScripts = {}

    def __init__(self):
        super().__init__()

    def run_new(self, args):
        """Starts a new script.

        Args:
            args: (Path, int), the path to the script,
                the timestamp of the ChildScript.
        """
        c = child_script.ChildScript(str(args[0]))
        c.start_script()
        self.currently_running_ChildScripts[args[1]] = c

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
                SetWindowPos(
                    window_handle,
                    HWND_NOTOPMOST,
                    0,
                    0,
                    0,
                    0,
                    SWP_SHOWWINDOW + SWP_NOMOVE + SWP_NOSIZE,
                )
