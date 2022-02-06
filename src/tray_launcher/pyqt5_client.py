import asyncio
import argparse
import os
import sys

from PyQt5.QtCore import QDataStream, QIODevice
from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtWidgets import QApplication, QMainWindow

class Client(QMainWindow):
    def __init__(self):
        super().init()
        super().resize(0, 0)
        self.show()
        self.client = QTcpSocket(self)
        self.client.connectToHost("127.0.0.1", 7686, QIODevice.ReadWrite)
        self.client.write("Hello".encode())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    c = Client()
    sys.exit(c.exec_())