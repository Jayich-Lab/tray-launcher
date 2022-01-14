from sys import argv, exit
from os import startfile
from time import time, localtime
from pathlib import Path
from functools import partial
from shutil import copy, SameFileError
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAction, QSystemTrayIcon, qApp, QApplication, QMessageBox, QMainWindow, QMenu, QFileDialog, QMessageBox, QWidget, QDesktopWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QIcon

from tray_launcher import core


class LauncherTray (QMainWindow):
    trayicon = None
    script_manager = None
    script_count = 0
    currently_running_scripts = {}      # key: int, value: QMenu
    available_scripts = {}              # key: str, value: QAction
    last_open = None

    def __init__(self):
        self.HOME_PATH = Path(core.__file__).parent
        self.USER = Path.home()

        self.USER_HOME = self.USER / "tray_launcher"
        self.LOGS = self.USER_HOME / "logs"
        self.AVAILABLE_SCRIPTS = self.USER_HOME / "available_scripts"

        self.icon = str(self.HOME_PATH / "icons" / "tray_icon.png")
        self.check_mark = str(self.HOME_PATH / "icons" / "check_mark.png")

        super().__init__()
        self.script_manager = core.ChildScriptManager()
        t = localtime(time())
        try:
            log_directory = self.LOGS / (str(t.tm_year) + "_" + str(t.tm_mon) + "_" + str(t.tm_mday))
            log_directory.mkdir(parents = True, exist_ok = True)
        except Exception as err:
            logging.error(err + ": Failed to create new directory for outputs")
            raise
        
        try:
            self.AVAILABLE_SCRIPTS.mkdir(parents = True, exist_ok = True)
        except Exception as err:
            logging.error(err + ": Failed to create new directory for available scripts")
            raise
        logging.basicConfig(filename = log_directory / "tray_launcher.log", level = logging.INFO, format = "%(asctime)s %(message)s")
        logging.info("Tray Launcher Started.")
        self.initUI()

    def initUI(self):
        self.trayicon = QSystemTrayIcon(self)
        self.trayicon.setIcon(QIcon(self.icon))
        self.trayicon.setVisible(True)

        self.context_menu = QMenu(self)
        load_new_script = QAction("Load New Script(s)", self)    
        load_new_script.triggered.connect(partial(self.load_scripts_from_file_dialogue, self.USER))

        self.view_all = QMenu("Start a Script", self)
        self.add_available_scripts(self.view_all)
        self.view_all.aboutToShow.connect(self.check_available_scripts)

        self.view_in_directory = self.view_all.addAction("[View in Directory]")
        self.view_in_directory.triggered.connect(partial(self.open_script_from_file_dialogue, self.AVAILABLE_SCRIPTS))

        self.currently_running_section = self.context_menu.addSection("Currently Running")

        self.none_currently_running = self.context_menu.addAction("None")
        self.none_currently_running.setEnabled(False)

        self.bottom_separator = self.context_menu.addSeparator()

        self.context_menu.addMenu(self.view_all)

        self.context_menu.addAction(load_new_script)

        logs = self.context_menu.addAction("All Logs")
        logs.triggered.connect(partial(self.showLogs, self.LOGS))

        help_ = self.context_menu.addAction("Help")
        help_.triggered.connect(self.showHelp)

        quit_ = self.context_menu.addAction("Quit")
        quit_.triggered.connect(self.quit)

        self.context_menu.aboutToShow.connect(self.prepare_context_menu)
        self.trayicon.setContextMenu(self.context_menu)
        self.show()
        super().resize(0,0)
        self.trayicon.show()

        tm = localtime(time())
        self.last_open = (tm.tm_year, tm.tm_mon, tm.tm_mday)

    def start_new_script(self, script_path):
        """Starts a new script.

        Args:
            script_path: Path, path to the script to be started.
        """
        script_path_str = str(script_path)

        timestamp = time()
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
        logAction.triggered.connect(partial(self.showLogs, self.script_manager.currently_running_ChildScripts[timestamp].log_path))
        three_menu.insertAction(restartAction, logAction)

        self.context_menu.insertMenu(self.bottom_separator, three_menu)
        self.currently_running_scripts[timestamp] = three_menu

        three_menu.menuAction().setIcon(QIcon(self.check_mark))
        self.available_scripts[script_path.name].setEnabled(False)

    def show_script(self, args):
        """Bring windows associated with a script to the foreground, if any.

        Args:
            args: (Path, int), the path to the script, the timestamp of the ChildScript.
        """
        self.run_in_manager(args, self.script_manager.show)
        # print(self.script_manager.currently_running_ChildScripts[args[1]].current_PIDs)

        logging.info("{} was brought to the front.".format(args[0].stem) + " Processes with PIDs {} are running.".format(self.script_manager.currently_running_ChildScripts[args[1]].current_PIDs))

    def terminate_script(self, args):
        """Terminate a script.

        Args:
            args: ((Path, int), QMenu), the path to the script, the timestamp of the ChildScript, and the QMenu associated with this script.
        """
        self.run_in_manager(args[0][1], self.script_manager.terminate)
        self.context_menu.removeAction(args[1].menuAction())
        del self.currently_running_scripts[args[0][1]]

        self.script_count -= 1

        if(self.script_count == 0):
            self.none_currently_running.setVisible(True)

        self.available_scripts[(args[0][0]).name].setIcon(QIcon())
        self.available_scripts[(args[0][0]).name].setEnabled(True)

        logging.info("{} was terminated through Tray Launcher.".format(args[0][0].stem))

    def restart_script(self, args):
        """Restarts a script.

        Args:
            args: ((str, int), QMenu), the path to the script, the timestamp of the ChildScript, and the QMenu associated with this script.
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

    def add_available_scripts(self, target_menu):
        """Loads all .bat files in the \available_scripts directory to the menu specified.

        Args:
            target_menu: QMenu, the menu to be loaded with .bat file stems.
        """
        for file_path in Path.iterdir(self.AVAILABLE_SCRIPTS):
            if(file_path.is_file() and file_path.suffix == ".bat"):
                action = target_menu.addAction(file_path.stem)
                action.triggered.connect(partial(self.start_new_script, file_path))
                self.available_scripts[file_path.name] = action 

                for menu in self.currently_running_scripts.values():
                    if(file_path.stem == menu.menuAction().text()):
                        self.available_scripts[file_path.name].setIcon(QIcon(self.check_mark))
                        self.available_scripts[file_path.name].setEnabled(False)
            else:
                if(file_path.is_file):
                   file_path.unlink()   #Not sure if this really REMOVEs the file

    def check_available_scripts(self):
        """Reloads .bat files in the \available_scripts directory to the view_all menu"""
        self.view_all.clear()

        self.add_available_scripts(self.view_all)

        self.view_in_directory = QAction("[View in Directory]", self)
        self.view_in_directory.triggered.connect(partial(self.open_script_from_file_dialogue, self.AVAILABLE_SCRIPTS))
        self.view_all.addAction(self.view_in_directory)

    def prepare_context_menu(self):
        """Starts a new log for this Tray Launcher for every new day. Checks if scripts are still running; if not, remove them from the menu."""
        tm = localtime(time())
        now = (tm.tm_year, tm.tm_mon, tm.tm_mday)
        if(now != self.last_open):
            self.last_open = now

            for handler in logging.root.handlers[:]:
                handler.close()
                logging.root.removeHandler(handler)

            try:
                log_directory = self.LOGS / (str(now[0]) + "_" + str(now[1]) + "_" + str(now[2]))
                log_directory.mkdir(parents = True, exist_ok = True)
            except Exception as err:
                logging.error(err + ": Failed to create new directory for outputs")
                raise

            logging.basicConfig(filename = log_directory / "tray_launcher.log", level = logging.INFO, format = "%(asctime)s %(message)s")

        to_del = []
        for timestamp, child_script in self.script_manager.currently_running_ChildScripts.items():
            if(not child_script.is_active()):
                child_script.outputs_file.close()
                # child_script.terminate_script()
                to_del.append(timestamp)
                self.context_menu.removeAction(self.currently_running_scripts[timestamp].menuAction())
                del self.currently_running_scripts[timestamp]

                self.script_count -= 1
                if(self.script_count == 0):
                    self.none_currently_running.setVisible(True)
                logging.info("{} has already been terminated. Now removed from the menu.".format(child_script.script_path_str))

        for ts in to_del:
            del self.script_manager.currently_running_ChildScripts[ts]

    def load_scripts_from_file_dialogue(self, dir):
        """
        Args:
            dir: Path, path of the directory from which a file is to be loaded.
        """
        fnames, _ = QFileDialog.getOpenFileNames(self, 'Loading New Script(s) (.bat only)', str(dir), ("Images (*.bat)"))

        for file_name in fnames:
            self.load_script(Path(file_name))

    def open_script_from_file_dialogue(self, file_dialogue_path):
        """Starts a file selected from the directory specified by the argument file_dialogue_path. If the file is not in the \available_files directory, load it.
        
        Args:
            file_dialogue_path: Path, path of the directory from which a file is to be loaded.
        """
        file_name, _ = QFileDialog.getOpenFileName(self, 'Starting a Script (.bat only)', str(file_dialogue_path), ("Images (*.bat)"))

        if (file_name != ""):
            file_path = Path(file_name)

            if(file_path.is_file() and file_path.suffix == ".bat" and file_path.parent == self.AVAILABLE_SCRIPTS):
                self.start_new_script(file_path)
            elif(file_path.is_file() and file_path.suffix == ".bat"):
                self.load_script(file_path)

                action = QAction(file_path.stem)
                action.triggered.connect(partial(self.start_new_script, file_path))
                self.available_scripts[file_path.name] = action

                self.start_new_script(file_path)
            else:
                logging.info("Only files in \\available_script are accepted.")

    def load_script(self, script_path):
        """Loads the specified file to the \available_scripts directory. If there is a file with the same name, asks the user if they wish to replace.

        Args:
            script_path: Path, the path to the file to be loaded.
        """
        isDuplicateName = False

        if(script_path.is_file() and script_path.suffix == ".bat"):
            for existing_file_path in Path.iterdir(self.AVAILABLE_SCRIPTS):
                if(existing_file_path == script_path):
                    isDuplicateName = True
                    break
        
        if(not isDuplicateName):
            copy(script_path, self.AVAILABLE_SCRIPTS)
            action = QAction(script_path.stem, self)
            action.triggered.connect(partial(self.start_new_script, script_path))
            self.view_all.insertAction(self.view_in_directory, action)
            logging.info("{} was loaded to \\available_scripts.".format(str(script_path)))
        else:
            self.resize(1,1)
            self.showMinimized()
            self.showMaximized()
            self.resize(0,0)
            b = QMessageBox()
            b.setWindowFlag(Qt.WindowStaysOnTopHint)
            replace_reply = b.question(self, "Replace File", "A file named {} already exists in \\available_scripts. Do you want to replace it?".format(script_path.name), 
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if(replace_reply == QMessageBox.Yes):
                try:
                    copy(script_path, self.AVAILABLE_SCRIPTS)
                    logging.info("{} was replaced in \\available_scripts.".format(str(script_path)))
                except SameFileError:
                    return
            else:
                return

    def quit(self):
        for timestamp in self.currently_running_scripts.keys():
            self.script_manager.terminate(timestamp)
        logging.info("Tray Launcher Exited.")
        self.script_manager.deleteLater()
        qApp.quit()

    def showLogs(self, log_path):
        """Displays the file specified.

        Args:
            log_path: Path, the path to the file to be opened.
        """
        logging.info("Logs {} were opened.".format(log_path))
        startfile(log_path)
    
    def showHelp(self):
        """Displays a Help window in the middle of the screen"""
        self.help_window = QWidget()
        self.help_window.resize(100, 100)

        Rect = self.help_window.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        Rect.moveCenter(center)
        self.help_window.move(Rect.topLeft())

        self.help_window.setWindowTitle("Help")
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("1. Load scripts by clicking the \"Load New Scripts(s)\" option \nand" 
                                   + " select scripts you wish to run in the future. \n2. Move over"
                                   + " \"Start a Script\" to select one script to run. \n3. If a problem"
                                   + " occurs, go find Tommy."))
        self.help_window.setLayout(layout)
        self.help_window.show()

def main():
        app = QApplication(argv)
        app.setStyle("Fusion")
        lc = LauncherTray()
        exit(app.exec_())

if __name__ == "__main__":
    main()