import argparse
import os

from PyQt5.QtCore import QDataStream, QIODevice, QObject
from PyQt5.QtNetwork import QTcpSocket


class TrayLauncherClient(QObject):
    def __init__(self, command, data):
        super().__init__()

        self.blockSize = 0

        self.client = QTcpSocket(self)
        self.client.readyRead.connect(self.read_from_server)
        
        self.client.connectToHost("127.0.0.1", int(os.environ.get("TRAY_LAUNCHER_PORT", 7686)), QIODevice.ReadWrite)
        self.client.waitForConnected()

        self.client.write(bytes(command + "\n", encoding="ascii"))

        for entry in data:
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