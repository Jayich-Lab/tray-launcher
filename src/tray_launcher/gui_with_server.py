import logging
import os
import asyncio
import shutil as _su
import subprocess
import sys
import time as _t
from functools import partial
from pathlib import Path

from PyQt5.QtCore import (
    Qt,
    QIODevice,
    QDataStream,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtNetwork import (QHostAddress, QTcpServer,)
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDesktopWidget,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
    qApp,
)

from tray_launcher import core


class LauncherTray(QMainWindow):
    trayicon = None
    script_manager = None
    script_count = 0

    # key: int, value: QMenu
        # key: timestamp
        # value: three_menu QMenu, which contains four actions haha
    # Contains all currently_running_scripts
    currently_running_scripts = {}

    # key: string:                          script.stem
    # value: tuple (int, QMenu):            (timestamp, three_menu)
    _currently_running_scripts = {}            


    # key: str, value: QAction
        # key: script.name
        # value: QAction
    # This is to show up in "Start a Script"
    available_scripts = {}

    def __init__(self):
        print("Test8")
        self.HOME_PATH = Path(core.__file__).parent
        self.USER = Path.home()

        self.USER_HOME = self.USER / ".tray_launcher"
        self.LOGS = self.USER_HOME / "logs"
        self.AVAILABLE_SCRIPTS = self.USER_HOME / "scripts"

        self.icon = str(self.HOME_PATH / "icons" / "tray_icon.png")
        self.check_mark = str(self.HOME_PATH / "icons" / "check_mark.png")

        super().__init__()
        self.script_manager = core.ChildScriptManager()
        t = _t.localtime(_t.time())
        try:
            log_directory = self.LOGS / (
                str(t.tm_year) + "_" + str(t.tm_mon).zfill(2) + "_" + str(t.tm_mday).zfill(2)
            )
            log_directory.mkdir(parents=True, exist_ok=True)
        except Exception as err:
            print(err + ": Failed to create new directory for outputs")
            raise

        try:
            self.AVAILABLE_SCRIPTS.mkdir(parents=True, exist_ok=True)
        except Exception as err:
            print(err + ": Failed to create new directory for available scripts")
            raise
        logging.basicConfig(
            filename=log_directory / "tray_launcher.log",
            level=logging.INFO,
            format="%(asctime)s %(message)s",
        )
        logging.info("Tray Launcher Started.")
        self.initUI()
        self.initServer()

    def processConnection(self):
        clientConnection = self.server.nextPendingConnection()

        clientConnection.waitForReadyRead()

        data = []
        while(not clientConnection.atEnd()):
            data.append(str(clientConnection.readLine(), encoding="ascii")[0:-1])

        print(data)

        clientConnection.disconnected.connect(clientConnection.deleteLater)
        clientConnection.disconnectFromHost()


        #Only the CLIENT can print to the screen, so write to the CLIENT!!
        if(data[0] == "start"):
            for p in data[1:]:
                file_path = Path(p)
                if(not (self.run_new_file(file_path) or self.run_new_file(self.to_loaded_path(file_path)))):
                    ## TO-DO: write to the client saying that p is not valid. "Only .bat file is accepted."
                    print("Bad")
                

        elif(data[0] == "terminate"):
            for p in data[1:]:
                full_path = self.toFullPath(p, True)
                if(full_path != None):
                    self.terminate_script() #Add those arguments. IMPORTANT: we might not have the info needed, so we have to change some old codes to preserve the info we need here: like which menu is associated with each childScript
                else:
                    #Write to the CLIENT saying that the requested script is not running
                    return
        elif(data[0] == "list"):
            self.check_available_scripts()
            return
        elif(data[0] == "load"):
            return
        elif(data[0] == "restart"):
            return
        elif(data[0] == "log"):
            return
        elif(data[0] == "front"):
            return
        elif(data[0] == "quit"):
            self.quick_quit()
            return

    #This is gonna be used in start_new_script(). No duplicate (even names) is allowed
    def isCurrentlyRunning(self, script_path):
        return

    #Should call add_available_scripts() to clear the "scripts" directory
    def to_loaded_path(self, str_given):
        '''Returns a Path
        '''
        print(str(Path(self.AVAILABLE_SCRIPTS / str_given).with_suffix(".bat")))
        return Path(self.AVAILABLE_SCRIPTS / str_given).with_suffix(".bat")




    def initServer(self):
        self.server = QTcpServer(self)
        port = int(os.environ.get("TRAY_LAUNCHER_PORT", 7686))
        address = QHostAddress("127.0.0.1")
        if(not self.server.listen(address, port)):
            logging.warning("Failed to listen to port: " + str(port) + ". See README.md to switch to an available port.")
            # We want to do more explicit warnings
            return
        self.server.newConnection.connect(self.processConnection)
            
    def initUI(self):
        self.trayicon = QSystemTrayIcon(self)
        self.trayicon.setIcon(QIcon(self.icon))
        self.trayicon.setVisible(True)

        self.context_menu = QMenu(self)
        load_new_script = QAction("Load New Script(s)", self)
        load_new_script.triggered.connect(partial(self.load_scripts_from_file_dialogue, self.USER))

        self.view_all = QMenu("Start a Script", self)
        self.add_available_scripts(self.view_all)
        # self.view_all.aboutToShow.connect(self.check_available_scripts)

        self.view_in_directory = self.view_all.addAction("[View in Directory]")
        self.view_in_directory.triggered.connect(
            partial(self.open_script_from_file_dialogue, self.AVAILABLE_SCRIPTS)
        )

        self.currently_running_section = self.context_menu.addSection("Currently Running")

        self.none_currently_running = self.context_menu.addAction("None")
        self.none_currently_running.setEnabled(False)

        self.bottom_separator = self.context_menu.addSeparator()

        self.context_menu.addMenu(self.view_all)

        self.context_menu.addAction(load_new_script)

        logs = self.context_menu.addAction("All Logs")
        logs.triggered.connect(partial(self.show_logs, self.LOGS))

        help_ = self.context_menu.addAction("Help")
        help_.triggered.connect(self.show_help)

        self.quit_ = self.context_menu.addAction("Quit")
        self.quit_.triggered.connect(self.quit)

        self.context_menu.aboutToShow.connect(self.prepare_context_menu)
        self.trayicon.setContextMenu(self.context_menu)

        self.check_available_scripts()
        self.show()
        super().resize(0, 0)
        self.trayicon.show()

    def start_new_script(self, script_path):
        """Starts a new script.

        Args:
            script_path: Path, path to the script to be started.
        """

        # if(script_path.stem in self.currently_running_scripts):
        #     print("Cannot run a script with the same stem as one of the currently running scripts!")
        #     return

        timestamp = _t.time()
        args = (script_path, timestamp)
        three_menu = QMenu(script_path.stem, self)

        showAction = QAction("Show", self)
        showAction.triggered.connect(partial(self.show_script, args))
        three_menu.addAction(showAction)

        restartAction = QAction("Restart", self)
        restartAction.triggered.connect(partial(self.restart_script, (args, three_menu)))
        three_menu.addAction(restartAction)

        terminateAction = QAction("Terminate", self)
        terminateAction.triggered.connect(partial(self.terminate_script, (args, three_menu)))
        three_menu.addAction(terminateAction)

        self.run_in_manager(args, self.script_manager.run_new)

        self.none_currently_running.setVisible(False)
        self.script_count += 1

        logging.info("{} was started.".format(script_path.stem))

        logAction = QAction("Log", self)
        logAction.triggered.connect(
            partial(
                self.show_logs,
                self.script_manager.currently_running_ChildScripts[timestamp].log_path,
            )
        )
        three_menu.insertAction(restartAction, logAction)

        self.context_menu.insertMenu(self.bottom_separator, three_menu)

        #self.currently_running_scripts[script_path.stem] = (timestamp, three_menu)
        self.currently_running_scripts[timestamp] = three_menu

        three_menu.menuAction().setIcon(QIcon(self.check_mark))
        self.available_scripts[script_path.stem].setEnabled(False)

    def show_script(self, args):
        """Bring windows associated with a script to the foreground, if any.

        Args:
            args: (Path, int), the path to the script, the timestamp of the ChildScript.
        """
        self.run_in_manager(args, self.script_manager.show)

        logging.info(
            "{} was brought to the front.".format(args[0].stem)
            + " Processes with PIDs {} are running.".format(
                self.script_manager.currently_running_ChildScripts[args[1]].current_PIDs
            )
        )

    def terminate_script(self, args):
        """Terminate a script.

        Args:
            args: ((Path, int), QMenu), the path to the script,
                the timestamp of the ChildScript, and the QMenu associated with this script.
        """
        #if(args[0][1].stem in self.currently_running_scripts):
        if(args[0][1] in self.currently_running_scripts):
            self.run_in_manager(args[0][1], self.script_manager.terminate)
            self.context_menu.removeAction(args[1].menuAction())

            #del self.currently_running_scripts[args[0][1].stem]
            del self.currently_running_scripts[args[0][1]]

            self.script_count -= 1

            if self.script_count == 0:
                self.none_currently_running.setVisible(True)

            # There was a bug associated with "deleting a file from the "scripts" directory when the file is running, then terminating this file", when without this if condition
            # The error:   in terminate_script self.available_scripts[(args[0][0]).name].setIcon(QIcon()) RuntimeError: wrapped C/C++ object of type QAction has been deleted

            # I thought adding this if condition would help, but after I added self.check_available_scripts() in load() and prepare_context_menu(), 
            # this bug disappeared even without the if. But for safety, I will keep it here.
            if((args[0][0]).stem in self.available_scripts):
                self.available_scripts[(args[0][0]).stem].setIcon(QIcon())
                self.available_scripts[(args[0][0]).stem].setEnabled(True)

            logging.info("{} was terminated through Tray Launcher.".format(args[0][0].stem))

        else:
            print("{} is not running.".format(args[0][0].stem))

    def restart_script(self, args):
        """Restarts a script.

        Args:
            args: ((str, int), QMenu), the path to the script, the timestamp of the ChildScript,
                and the QMenu associated with this script.
        """
        self.terminate_script(args)
        self.start_new_script(args[0][0])

        logging.info("{} was restarted.".format(args[0][0].stem))

    def run_in_manager(self, args, func):
        """Runs a function through the script manager.

        Args:
            args: (str, int), the path to the script, the timestamp of the ChildScript.
            func: an instance function of ChildScriptManager.
        """
        dummy_action = QAction(self)
        dummy_action.triggered.connect(partial(func, args))
        dummy_action.trigger()

    # This is an important reset method. Coordinate with this
    def add_available_scripts(self, target_menu):
        """Loads all .bat files in the \\scripts directory to the menu specified.

        Args:
            target_menu: QMenu, the menu to be loaded with .bat file stems.
        """
        self.available_scripts.clear()
        target_menu.clear()

        for file_path in Path.iterdir(self.AVAILABLE_SCRIPTS):
            if file_path.is_file() and file_path.suffix == ".bat":
                action = target_menu.addAction(file_path.stem)
                action.triggered.connect(partial(self.start_new_script, file_path))
                self.available_scripts[file_path.stem] = action

                for menu in self.currently_running_scripts.values():
                    #menu = entry[1]
                    if file_path.stem == menu.menuAction().text():
                        self.available_scripts[file_path.stem].setIcon(QIcon(self.check_mark))
                        self.available_scripts[file_path.stem].setEnabled(False)
            else:
                if file_path.is_file:
                    file_path.unlink()

    # When loaded scripts abount, this function may cost a more significant amount of time
    def check_available_scripts(self):
        """Reloads .bat files in the \\scripts directory to the view_all menu"""
        self.add_available_scripts(self.view_all)

        self.view_in_directory = QAction("[View in Directory]", self)
        self.view_in_directory.triggered.connect(
            partial(self.open_script_from_file_dialogue, self.AVAILABLE_SCRIPTS)
        )
        self.view_all.addAction(self.view_in_directory)

    def prepare_context_menu(self):
        """Checks if scripts are still running; if not, remove them from the menu.
        Also rebuilds the the view_all menu    
        """
        to_del = []
        for timestamp, child_script in self.script_manager.currently_running_ChildScripts.items():
            if not child_script.is_active():
                child_script.outputs_file.close()

                to_del.append(timestamp)
                self.context_menu.removeAction(
                    #self.currently_running_scripts[child_script.script_path.stem][1].menuAction()
                    self.currently_running_scripts[timestamp].menuAction()
                )
                # del self.currently_running_scripts[child_script.script_path.stem]
                del self.currently_running_scripts[timestamp]

                self.script_count -= 1
                if self.script_count == 0:
                    self.none_currently_running.setVisible(True)
                logging.info(
                    "{} has already been terminated. Now removed from the menu.".format(
                        child_script.script_path_str
                    )
                )

        for ts in to_del:
            del self.script_manager.currently_running_ChildScripts[ts]

        self.check_available_scripts()

    def load_scripts_from_file_dialogue(self, dir):
        """
        Args:
            dir: Path, path of the directory from which a file is to be loaded.
        """
        fnames, _ = QFileDialog.getOpenFileNames(
            self, "Loading New Script(s) (.bat only)", str(dir), ("Images (*.bat)")
        )

        for file_name in fnames:
            self.load_script(Path(file_name))

    def open_script_from_file_dialogue(self, file_dialogue_path):
        """Starts a file selected from the directory specified
            by the argument file_dialogue_path.
            If the file is not in the \\scripts directory, load it.

        Args:
            file_dialogue_path: Path, path of the directory from which a file is to be loaded.
        """
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Starting a Script (.bat only)", str(file_dialogue_path), ("Images (*.bat)")
        )

        if file_name != "":
            file_path = Path(file_name)

            self.run_new_file(file_path)

    def run_new_file(self, file_path):
        '''

        Args: Path
        '''
        if(not (file_path.is_file() and file_path.suffix == ".bat")):
            logging.info("Only .bat file is accepted.")
            print("Only .bat file is accepted.")
            return False

        elif (file_path.parent == self.AVAILABLE_SCRIPTS):
                self.check_available_scripts()
                self.start_new_script(file_path)
                return True
        else:
            if(self.load_script(file_path)):
                file_path = self.to_loaded_path(file_path.stem)

                # #
                # action = QAction(file_path.stem, self)    #This "self" was not here
                # action.triggered.connect(partial(self.start_new_script, file_path))
                # self.available_scripts[file_path.name] = action
                # #
                self.start_new_script(file_path)
            return True
            

    def load_script(self, script_path):
        """Loads the specified file to the \\scripts directory.
            If there is a file with the same name, asks the user
            if they wish to replace.

        Args:
            script_path: Path, the path to the file to be loaded.
        """
        isDuplicateName = False

        if script_path.is_file() and script_path.suffix == ".bat":
            for existing_file_path in Path.iterdir(self.AVAILABLE_SCRIPTS):
                if existing_file_path.stem == script_path.stem:
                    isDuplicateName = True
                    break

        if not isDuplicateName:
            _su.copy(script_path, self.AVAILABLE_SCRIPTS)

            # # It is strange that I didn't add to __available_scripts__ dict here
            # action = QAction(script_path.stem, self)
            # action.triggered.connect(partial(self.start_new_script, script_path))
            # self.view_all.insertAction(self.view_in_directory, action)  #But, is this "action" in __available_scripts__ dict?
            # #

            logging.info("{} was loaded to \\scripts.".format(str(script_path)))
            self.check_available_scripts()
            return True
        else:
            self.resize(1, 1)
            self.showMinimized()
            self.showMaximized()
            self.resize(0, 0)
            b = QMessageBox()
            b.setWindowFlag(Qt.WindowStaysOnTopHint)
            replace_reply = b.question(
                self,
                "Replace File",
                "A file named {} already exists in "
                "\\scripts. Do you want to replace it?".format(script_path.name),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if replace_reply == QMessageBox.Yes:
                try:
                    _su.copy(script_path, self.AVAILABLE_SCRIPTS)
                    logging.info("{} was replaced in \\scripts.".format(str(script_path)))
                    self.check_available_scripts()
                    return True
                except _su.SameFileError:
                    print("Same File!")
                    return True
            else:
                return False

    def quit(self):
        self.resize(1, 1)
        self.showMinimized()
        self.showMaximized()
        self.resize(0, 0)
        b = QMessageBox()
        b.setWindowFlag(Qt.WindowStaysOnTopHint)
        replace_reply = b.question(
            self,
            "Quit Tray Launcher",
            "Do you want to quit tray launcher?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if replace_reply == QMessageBox.Yes:
            for timestamp in self.currently_running_scripts.keys():
                self.script_manager.terminate(timestamp)

            # for tuple in self.currently_running_scripts.values():
            #     self.script_manager.terminate(tuple[0])
            logging.info("Tray Launcher Exited.")
            self.script_manager.deleteLater()
            qApp.quit()
    
    def quick_quit(self):
        for timestamp in self.currently_running_scripts.keys():
            self.script_manager.terminate(timestamp)
        
        # for tuple in self.currently_running_scripts.values():
            #self.script_manager.terminate(tuple[0])
        logging.info("Tray Launcher Exited.")
        self.script_manager.deleteLater()
        qApp.quit()

    def show_logs(self, log_path):
        """Displays the file specified.

        Args:
            log_path: Path, the path to the file to be opened.
        """
        logging.info("Logs {} were opened.".format(log_path))
        os.startfile(log_path)

    def show_help(self):
        """Displays a Help window in the middle of the screen"""
        self.help_window = QWidget()
        self.help_window.resize(100, 100)

        Rect = self.help_window.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        Rect.moveCenter(center)
        self.help_window.move(Rect.topLeft())

        self.help_window.setWindowTitle("Help")

        layout = QVBoxLayout()
        layout.addWidget(
            QLabel(
                '1. Load scripts by clicking the "Load New Scripts(s)" option \nand'
                + " select scripts you wish to run in the future. \n2. Move over"
                + ' "Start a Script" to select one script to run. \n3. If a problem'
                + " occurs, go find Tommy."
            )
        )
        self.help_window.setLayout(layout)
        self.help_window.show()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    lc = LauncherTray()
    lc.show()
    
    sys.exit(app.exec_())

    


def run_pythonw():
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
            "python " + str(HOME_PATH),
            encoding="utf-8",
            creationflags=subprocess.CREATE_NO_WINDOW,
            # this file is being written both by this stderr
            # and the logging in the LauncherTray class
            stdout=launcher_log,
            stderr=launcher_log,
        )

    print("Tray Launcher is running...")


if __name__ == "__main__":
    main()
