import logging
import os
import sys
import subprocess
import time as _t

from pathlib import Path
from functools import partial

from PyQt5.QtNetwork import QHostAddress, QTcpServer
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QByteArray, QDataStream, QIODevice, Qt
from PyQt5.QtWidgets import QApplication, qApp

from tray_launcher import gui, tray_launcher_client

class TrayLauncherCLI():
    def __init__(self):
        self.message_to_client = []

        self.server = QTcpServer(self)
        port = int(os.environ.get("TRAY_LAUNCHER_PORT", 7686))
        address = QHostAddress("127.0.0.1")
        if not self.server.listen(address, port):
            logging.warning(
                "Failed to listen to port: "
                + str(port)
                + ". See README.md to switch to an available port."
            )
            return
        self.server.newConnection.connect(self.process_connection)

        self.gui = gui.TrayLauncher()

    def process_connection(self):
        """Processes the list passed from the client, and writes response back."""
        client_connection = self.server.nextPendingConnection()

        client_connection.waitForReadyRead()

        data = []
        while not client_connection.atEnd():
            data.append(str(client_connection.readLine(), encoding="ascii")[0:-1])

        dispatchers = {
            "test": self.prcess_test,
            "start": self.process_start,
            "terminate": self.process_terminate,
            "list": self.process_list,
            "list_current": self.process_list_current,
            "load": self.process_load,
            "restart": self.process_restart,
            "log": self.process_log,
            "all_logs": self.process_all_logs,
            "focus": self.process_focus,
            "quit": self.process_quit,
        }

        try:
            dispatcher = dispatchers[data[0]]
            dispatcher(data)
        except KeyError:
            self.process_invalid_command(data)

        self.write_to_client(client_connection)
        client_connection.disconnected.connect(client_connection.deleteLater)
        client_connection.disconnectFromHost()

    def prcess_test(self, data):
        """Processes the "test" command."""
        self.message_to_client.append(" ")

    def process_start(self, data):
        """Process the "start" command. Start new scripts."""
        for path_str in data[1:]:
            file_path = self.to_loaded_path(Path(path_str))
            if file_path is not None:
                if self.gui.run_new_file(file_path):
                    self.message_to_client.append("SUCCESS: {} is now running.".format(path_str))
                else:
                    self.message_to_client.append(
                        "{} is not valid. Only .bat files are accepted.".format(path_str)
                    )
            else:
                self.message_to_client.append("{} is not valid.".format(path_str))

    def process_terminate(self, data):
        """Process the "terminate" command. Terminate scripts that are running."""
        for path_str in data[1:]:
            file_path = self.to_loaded_path(Path(path_str))
            if file_path is not None:
                if (
                    file_path.is_file()
                    and file_path.parent == self.gui.AVAILABLE_SCRIPTS
                    and file_path.stem in self.gui.currently_running_scripts
                ):
                    self.gui.terminate_script(
                        (
                            (file_path, self.gui.currently_running_scripts[file_path.stem][0]),
                            self.gui.currently_running_scripts[file_path.stem][1],
                        )
                    )
                    self.message_to_client.append("SUCCESS: {} is now terminated.".format(path_str))
                elif file_path.is_file() and file_path.parent == self.gui.AVAILABLE_SCRIPTS:
                    self.message_to_client.append("{} is not running.".format(path_str))
                else:
                    self.message_to_client.append("{} is not valid.".format(path_str))
            else:
                self.message_to_client.append("{} is not valid.".format(path_str))

    def process_list(self, data):
        """Processes the "list -a" command. Writes loaded scripts' stems to the string
        which will be written back to the client.
        """
        self.gui.available_scripts.clear()
        self.gui.view_all.clear()

        for file_path in Path.iterdir(self.gui.AVAILABLE_SCRIPTS):
            if file_path.is_file() and file_path.suffix == ".bat":
                st = file_path.stem

                action = self.gui.view_all.addAction(st)
                action.triggered.connect(partial(self.gui.start_new_script, file_path))
                self.gui.available_scripts[st] = action

                if st in self.gui.currently_running_scripts:
                    self.gui.available_scripts[st].setIcon(QIcon(self.gui.check_mark))
                    self.gui.available_scripts[st].setEnabled(False)

                    self.message_to_client.append(
                        "{} \t \t \t \t \t \t(currently-running)".format(st)
                    )
                else:
                    self.message_to_client.append("{}".format(st))
            else:
                if file_path.is_file:
                    file_path.unlink()

    def process_list_current(self, data):
        """Processes the "list -r" command. Writes currently running scripts' stems to the string
        which will be written back to the client.
        """
        self.gui.available_scripts.clear()
        self.gui.view_all.clear()

        for file_path in Path.iterdir(self.gui.AVAILABLE_SCRIPTS):
            if file_path.is_file() and file_path.suffix == ".bat":
                st = file_path.stem

                action = self.gui.view_all.addAction(st)
                action.triggered.connect(partial(self.gui.start_new_script, file_path))
                self.gui.available_scripts[st] = action

                if st in self.gui.currently_running_scripts:
                    self.gui.available_scripts[st].setIcon(QIcon(self.gui.check_mark))
                    self.gui.available_scripts[st].setEnabled(False)

                    self.message_to_client.append("{}".format(st))
            else:
                if file_path.is_file:
                    file_path.unlink()

    def process_load(self, data):
        """Processes the "load" command. Loads scripts to the 'scripts' directory"""
        for path_str in data[1:]:
            file_path = Path(path_str)
            if not (self.gui.load_script(file_path)):
                self.message_to_client.append(
                    "{} is not loaded. (Only .bat file is accepted)".format(path_str)
                )
            else:
                self.message_to_client.append("SUCCESS: {} is loaded.".format(path_str))

    def process_restart(self, data):
        """Processes the "restart" command. Restarts scripts."""
        for path_str in data[1:]:
            file_path = self.to_loaded_path(Path(path_str))
            if file_path is not None:
                if (
                    file_path.is_file()
                    and file_path.parent == self.gui.AVAILABLE_SCRIPTS
                    and file_path.stem in self.gui.currently_running_scripts
                ):
                    self.gui.restart_script(
                        (
                            (file_path, self.gui.currently_running_scripts[file_path.stem][0]),
                            self.gui.currently_running_scripts[file_path.stem][1],
                        )
                    )
                    self.message_to_client.append("SUCCESS: {} is restarted.".format(path_str))
                elif file_path.is_file() and file_path.parent == self.gui.AVAILABLE_SCRIPTS:
                    self.message_to_client.append("{} is not running.".format(path_str))
                else:
                    self.message_to_client.append("{} is not valid.".format(path_str))
            else:
                self.message_to_client.append("{} is not valid.".format(path_str))

    def process_log(self, data):
        """Processes the "log" command. Brings up the log file of the scripts."""
        for path_str in data[1:]:
            if path_str == "tray-launcher":
                self.gui.show_logs(self.gui._log_directory / "tray_launcher.log")
                self.message_to_client.append("SUCCESS: Log of this tray launcher is shown.")
            else:
                file_path = self.to_loaded_path(Path(path_str))
                if file_path is not None:
                    if (
                        file_path.is_file()
                        and file_path.parent == self.gui.AVAILABLE_SCRIPTS
                        and file_path.stem in self.gui.currently_running_scripts
                    ):
                        self.gui.show_logs(
                            self.gui.script_manager.running_child_scripts[
                                self.gui.currently_running_scripts[file_path.stem][0]
                            ].log_path
                        )
                        self.message_to_client.append(
                            "SUCCESS: log of {} is shown.".format(path_str)
                        )
                    elif file_path.is_file() and file_path.parent == self.gui.AVAILABLE_SCRIPTS:
                        self.message_to_client.append("{} is not running.".format(path_str))
                    else:
                        self.message_to_client.append("{} is not valid.".format(path_str))
                else:
                    self.message_to_client.append("{} is not valid.".format(path_str))

    def process_all_logs(self, data):
        self.gui.show_logs(self.gui.LOGS)
        self.message_to_client.append("SUCCESS: all logs are shown.")

    def process_focus(self, data):
        """Processes the "focus" command. Brings the scripts to the foreground."""
        for path_str in data[1:]:
            file_path = self.to_loaded_path(Path(path_str))
            if file_path is not None:
                if (
                    file_path.is_file()
                    and file_path.parent == self.gui.AVAILABLE_SCRIPTS
                    and file_path.stem in self.gui.currently_running_scripts
                ):
                    self.gui.show_script((file_path, self.gui.currently_running_scripts[file_path.stem][0]))
                    self.message_to_client.append(
                        "SUCCESS: {} is now brought to the front.".format(path_str)
                    )
                elif file_path.is_file() and file_path.parent == self.gui.AVAILABLE_SCRIPTS:
                    self.message_to_client.append("{} is not running.".format(path_str))
                else:
                    self.message_to_client.append("{} is not valid.".format(path_str))
            else:
                self.message_to_client.append("{} is not valid.".format(path_str))

    def process_quit(self, data):
        """Processes the "quit" command. Quits the tray launcher without prompting."""
        for tuple in self.gui.currently_running_scripts.values():
            self.gui.script_manager.terminate(tuple[0])
        logging.info("Tray Launcher Exited.")
        self.gui.script_manager.deleteLater()
        qApp.quit()

    def process_invalid_command(self, data):
        """Processes an invalid command."""
        self.message_to_client.append("{} is an invalid command.".format(data[0]))

    def write_to_client(self, connection):
        """Passes the string (self.message_to_client) created by the server to the client."""

        if not self.message_to_client:
            return

        message = "\n".join(self.message_to_client)
        self.message_to_client = []

        block = QByteArray()
        out = QDataStream(block, QIODevice.ReadWrite)
        out.setVersion(QDataStream.Qt_5_0)
        out.writeUInt16(0)
        message = bytes(message, encoding="ascii")
        out.writeString(message)
        out.device().seek(0)
        out.writeUInt16(block.size() - 2)
        connection.write(block)

    def to_loaded_path(self, path_given):
        """Returns a Path that resembles one pointing to the "scripts" directory.
            Changes the parent of the path_given to the "scripts" directory and modifies its
            suffix to .bat

        Args:
            path_given: Path
        """
        try:
            loaded_path = Path(self.gui.AVAILABLE_SCRIPTS / path_given).with_suffix(".bat")
        except ValueError:
            return None
        return loaded_path


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    lc = TrayLauncherCLI()
    sys.exit(app.exec_())

def run_pythonw():
    instance_already_exists = tray_launcher_client.TrayLauncherClient.check_connection()
    if instance_already_exists:
        print("There is already an instance of tray launcher running. Terminating now.")
        return

    HOME_PATH = Path(__file__).parent / "gui.py"

    t = _t.localtime(_t.time())
    try:
        log_directory = (
            Path.home()
            / ".tray_launcher"
            / "logs"
            / (str(t.tm_year) + "_" + str(t.tm_mon).zfill(2) + "_" + str(t.tm_mday).zfill(2))
        )
        log_directory.mkdir(parents=True, exist_ok=True)
    except Exception as err:
        print(err + ": Failed to create new directory for outputs")
        raise
    with open(log_directory / "tray_launcher.log", "a") as launcher_log:
        subprocess.Popen(
            "python " + '"' + str(HOME_PATH) + '"',
            encoding="utf-8",
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=launcher_log,
            stderr=launcher_log,
        )

    print("Tray Launcher is running...")


if __name__ == "__main__":
    main()
