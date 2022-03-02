import logging
import os
import subprocess
import sys
import time as _t
from functools import partial
from pathlib import Path

from PyQt5.QtCore import QByteArray, QDataStream, QIODevice, QObject
from PyQt5.QtGui import QIcon
from PyQt5.QtNetwork import QHostAddress, QTcpServer
from PyQt5.QtWidgets import QApplication, qApp

from tray_launcher import gui, tray_launcher_client


class TrayLauncherCLI(QObject):
    def __init__(self):
        super().__init__()
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

        self.gui = gui.TrayLauncherGUI()

    def process_connection(self):
        """Processes the list passed from the client, and writes response back."""
        client_connection = self.server.nextPendingConnection()

        client_connection.waitForReadyRead()

        data = []
        while not client_connection.atEnd():
            data.append(str(client_connection.readLine(), encoding="ascii")[0:-1])

        dispatchers = {
            "test": self.test,
            "start": self.start,
            "terminate": self.terminate,
            "list": self.list_all,
            "list_current": self.list_current,
            "load": self.load,
            "restart": self.restart,
            "log": self.log,
            "all_logs": self.all_logs,
            "focus": self.focus,
            "quit": self.quit,
        }

        try:
            dispatcher = dispatchers[data[0]]
            dispatcher(data)
        except KeyError:
            self.process_invalid_command(data)

        self.write_to_client(client_connection)
        client_connection.disconnected.connect(client_connection.deleteLater)
        client_connection.disconnectFromHost()

    def test(self, data):
        """Processes the "test" command."""
        self.message_to_client.append(" ")

    def start(self, data):
        """Process the "start" command. Start new scripts."""
        for path_str in data[1:]:
            file_path = self.gui.to_loaded_path(Path(path_str))
            if file_path is not None:
                if file_path.stem in self.gui.currently_running_scripts:
                    self.message_to_client.append(
                        "Cannot run "
                        + "a script with the same stem as one of the currently running scripts."
                    )
                    return
                if self.gui.run_new_file(file_path):
                    self.message_to_client.append("SUCCESS: {} is now running.".format(path_str))
                else:
                    self.message_to_client.append(
                        "{} is not valid. Only .bat files are accepted.".format(path_str)
                    )
            else:
                self.message_to_client.append("{} is not valid.".format(path_str))

    def terminate(self, data):
        """Process the "terminate" command. Terminate scripts that are running."""
        for path_str in data[1:]:
            self.place_holder(self.gui.terminate_script, path_str, " is terminated.")

    def list_all(self, data):
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
                        "{} \t \t \t \t \t \t(currently running)".format(st)
                    )
                else:
                    self.message_to_client.append("{}".format(st))
            else:
                if file_path.is_file:
                    file_path.unlink()

    def list_current(self, data):
        """Processes the "list -r" command. Writes currently running scripts' stems to the string
        which will be written back to the client.
        """
        for st in self.gui.currently_running_scripts:
            self.message_to_client.append("{}".format(st))

    def load(self, data):
        """Processes the "load" command. Loads scripts to the 'scripts' directory"""
        for path_str in data[1:]:
            file_path = Path(path_str)
            if not (self.gui.load_script(file_path)):
                self.message_to_client.append(
                    "{} is not loaded. (Only .bat file is accepted)".format(path_str)
                )
            else:
                self.message_to_client.append("SUCCESS: {} is loaded.".format(path_str))

    def restart(self, data):
        """Processes the "restart" command. Restarts scripts."""
        for path_str in data[1:]:
            self.place_holder(self.gui.restart_script, path_str, " is restarted.")

    def log(self, data):
        """Processes the "log" command. Brings up the log file of the scripts."""
        for path_str in data[1:]:
            self.place_holder(self.gui.show_logs, path_str, "")

    def all_logs(self, data):
        self.gui.show_logs(self.gui.LOGS)
        self.message_to_client.append("SUCCESS: all logs are shown.")

    def focus(self, data):
        """Processes the "focus" command. Brings the scripts to the foreground."""
        for path_str in data[1:]:
            self.place_holder(self.gui.show_script, path_str, " is brought to the front.")

    def quit(self, data):
        """Processes the "quit" command. Quits the tray launcher without prompting."""
        for tuple in self.gui.currently_running_scripts.values():
            self.gui.script_manager.terminate(tuple[0])
        logging.info("Tray Launcher Exited.")
        self.gui.script_manager.deleteLater()
        qApp.quit()

    def process_invalid_command(self, data):
        """Processes an invalid command."""
        self.message_to_client.append("{} is an invalid command.".format(data[0]))

    def place_holder(self, func, path_str, success_message):
        file_path = self.gui.to_loaded_path(Path(path_str))
        if file_path is not None:
            if (
                file_path.is_file()
                and file_path.parent == self.gui.AVAILABLE_SCRIPTS
                and file_path.stem in self.gui.currently_running_scripts
            ):
                if func == self.gui.show_logs:
                    self.gui.show_logs(
                        self.gui.script_manager.running_child_scripts[
                            self.gui.currently_running_scripts[file_path.stem][0]
                        ].log_path
                    )
                    self.message_to_client.append(
                        "SUCCESS: log of {} is shown.".format(file_path.stem)
                    )
                else:
                    func(
                        (
                            (file_path, self.gui.currently_running_scripts[file_path.stem][0]),
                            self.gui.currently_running_scripts[file_path.stem][1],
                        )
                    )
                    self.message_to_client.append(
                        "SUCCESS: {}".format(file_path.stem) + success_message
                    )
            elif file_path.is_file() and file_path.parent == self.gui.AVAILABLE_SCRIPTS:
                self.message_to_client.append("{} is not running.".format(path_str))
            else:
                self.message_to_client.append("{} is not valid.".format(path_str))
        else:
            self.message_to_client.append("{} is not valid.".format(path_str))

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


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    lc = TrayLauncherCLI()
    sys.exit(app.exec_())
    lc.deleteLater()


def run_pythonw():
    instance_already_exists = tray_launcher_client.TrayLauncherClient.check_connection()
    if instance_already_exists:
        print("There is already an instance of tray launcher running. Terminating now.")
        return

    HOME_PATH = Path(__file__).parent / "cli.py"

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
