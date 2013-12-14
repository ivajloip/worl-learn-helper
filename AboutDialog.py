from PyQt4 import QtCore, QtGui

class AboutDialog(QtGui.QDialog):

  def __init__(self, message, parent = None):
    super(AboutDialog, self).__init__(parent)
    self.setWindowTitle(self.tr('About'))

    layout = QtGui.QVBoxLayout(self)
    self.setLayout(layout)

    text = QtGui.QTextEdit()
    text.setReadOnly(True)
    text.setText(message)

    ok_button = QtGui.QPushButton(self.tr('Ok'), self)
    ok_button.clicked.connect(self.ok_button_clicked)

    layout.addWidget(text)
    layout.addWidget(ok_button)

  def ok_button_clicked(self):
    self.accept()
