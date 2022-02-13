import asyncio
import argparse
import os
import sys

from PyQt5.QtCore import QDataStream, QIODevice, QCoreApplication, QObject
from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtWidgets import QApplication, QMainWindow

class TrayLauncherClient(QObject):
    def __init__(self, command, data):
        super().__init__()

        self.blockSize = 0

        self.client = QTcpSocket(self)
        self.client.connectToHost("127.0.0.1", 7686, QIODevice.ReadWrite)
        self.client.waitForConnected()

        self.client.write(bytes(command + "\n", encoding="ascii"))

        for entry in data:
            self.client.write(bytes((entry+ "\n"), encoding="ascii"))

        self.client.readyRead.connect(self.read_from_server)
        self.client.waitForDisconnected()
    


    # Copied from: https://stackoverflow.com/questions/41167409/pyqt5-sending-and-receiving-messages-between-client-and-server
    def read_from_server(self):
        instr = QDataStream(self.client)
        instr.setVersion(QDataStream.Qt_5_0)
        if self.blockSize == 0:
            if self.client.bytesAvailable() < 2:
                return
            self.blockSize = instr.readUInt16()
        if self.client.bytesAvailable() < self.blockSize:
            return
        # Print response to terminal, we could use it anywhere else we wanted.
        print(str(instr.readString(), encoding='ascii'))



def main():

    #Automatically takes as raw string, with \\
    parser = argparse.ArgumentParser(prog="tray_launcher", description="Manage scripts with the tray launcher.")

    parser.add_argument("-s", "--start", nargs="*", metavar="script_stem", type=str, help="Start new script(s).")   #Be able to start multiple scripts in one command line. Exhibit same behavior as if "View in Directory" so can add new scripts to the "scripts"

    parser.add_argument("-t", "--terminate", nargs="*", metavar="script_stem", type=str, help="Terminate the script specified.")

    parser.add_argument("-L", "--list", action="store_true", help="List all loaded scripts.")   #Should supply an option to only view "currently running"

    parser.add_argument("-l", "--list-current", action="store_true", help="List all currently running scripts.")   #Should supply an option to only view "currently running"

    parser.add_argument("--load", nargs="*", metavar="script_path", type=str, help="Load some scripts.")

    parser.add_argument("-r", "--restart", nargs="*", metavar="script_stem", type=str, help="Restart the script specified.")

    parser.add_argument("--log", nargs="*", metavar="script_stem", type=str, help="View log of the specified script.")      # This specified script has to be running. If no additional argument is given, do "View All". If parser.log=="tray_launcher", show self logs.

    parser.add_argument("-f", "--front", nargs="*", metavar="script_stem", type=str, help="Bring the specified script to the foreground.")

    parser.add_argument("-q", "--quit", action="store_true", help="Quit the tray launcher.")


    args = parser.parse_args()

    if args.load != None:
        print("Loading {}.".format(args.load))
        TrayLauncherClient("load", args.load)

    if args.start != None:
        print("Starting {}.".format(args.start))
        TrayLauncherClient("start", args.start)

    if args.log != None:
        print("Showing log of {}.".format(args.log))
        TrayLauncherClient("log", args.log)

    if args.restart != None:
        print("Restarting {}.".format(args.restart))
        TrayLauncherClient("restart", args.restart)

    if args.front != None:
        print("Bringing {} to the foreground.".format(args.front))
        TrayLauncherClient("front", args.front)

    if args.terminate != None:
        print("Terminating {}.".format(args.terminate))
        TrayLauncherClient("terminate", args.terminate)

    if args.list == True:
        print("Available scripts: ")
        TrayLauncherClient("list", [])
    
    if args.list_current == True:
        print("Currently running scripts: ")
        TrayLauncherClient("list_current", [])

    if args.quit == True:
        print("Quiting tray launcher.")
        TrayLauncherClient("quit", [])

    
if __name__ == "__main__":
    main()