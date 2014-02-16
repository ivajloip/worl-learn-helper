#!/usr/bin/python3

import MainWindow
import sys

from PyQt4 import QtCore, QtGui

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    window = MainWindow.MainWindow()
    sys.exit(app.exec_())       
