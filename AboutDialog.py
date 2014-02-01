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

    okButton = QtGui.QPushButton(self.tr('Ok'), self)
    okButton.clicked.connect(self.okButtonClicked)

    layout.addWidget(text)
    layout.addWidget(okButton)

  def okButtonClicked(self):
    self.accept()
