import os

from PyQt5.QtCore import QDataStream, QIODevice, QObject
from PyQt5.QtNetwork import QTcpSocket


class TrayLauncherClient(QObject):
    def __init__(self, command, data):
        """Initiate the client.

        Args:
            command: str
            data: str
        """
        super().__init__()

        self.blockSize = 0

        self.client = QTcpSocket(self)

        self.command = command
        self.data = data

    def check_connection(self):
        """Attempts to connect to the tray launcher TCP server
        to check if there is already one tray launcher instance running
        """
        self.command = "test"
        self.data = "empty"
        self.client.connectToHost(
            "127.0.0.1", int(os.environ.get("TRAY_LAUNCHER_PORT", 7686)), QIODevice.ReadWrite
        )
        success_connect = self.client.waitForConnected()

        if not success_connect:
            return False
        else:
            self.client.write(bytes(self.command + "\n", encoding="ascii"))
            self.client.write(bytes((self.data + "\n"), encoding="ascii"))
            self.client.waitForDisconnected()
            return True

    def attempt_connect(self):
        """Connects to the tray launcher server."""
        self.client.connectToHost(
            "127.0.0.1", int(os.environ.get("TRAY_LAUNCHER_PORT", 7686)), QIODevice.ReadWrite
        )
        success_connect = self.client.waitForConnected()

        if not success_connect:
            print(
                (
                    "Failed to connect to the launcher server. Run tray launcher first,"
                    " and check if the port supposedly used by the tray launcher is occupied."
                )
            )
            return

        self.client.readyRead.connect(self.read_from_server)

        self.client.write(bytes(self.command + "\n", encoding="ascii"))

        for entry in self.data:
            self.client.write(bytes((entry + "\n"), encoding="ascii"))

        self.client.waitForDisconnected()

    def read_from_server(self):
        instr = QDataStream(self.client)
        instr.setVersion(QDataStream.Qt_5_0)
        if self.blockSize == 0:
            if self.client.bytesAvailable() < 2:
                return
            self.blockSize = instr.readUInt16()
        if self.client.bytesAvailable() < self.blockSize:
            return
        print(str(instr.readString(), encoding="ascii"))
