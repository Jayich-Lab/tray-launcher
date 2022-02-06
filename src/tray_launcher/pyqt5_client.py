import asyncio
import argparse
import os
import sys

from PyQt5.QtCore import QDataStream, QIODevice, QCoreApplication, QObject
from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtWidgets import QApplication, QMainWindow

class Client(QObject):
    def __init__(self, ap):
        super().__init__()
        self.client = QTcpSocket(self)
        self.client.connectToHost("127.0.0.1", 7686, QIODevice.ReadWrite)
        self.client.write("Hello".encode())
        self.client.disconnected.conect(QCoreApplication.quit)

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    c = Client(app)
    sys.exit(app.exec_())