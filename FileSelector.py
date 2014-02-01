from PyQt4 import QtCore, QtGui

class FileSelector(QtGui.QWidget):
  def __init__(self, text, savedDir = '', parent = None):
    super(FileSelector, self).__init__(parent)

    soundDirectoryLayout = QtGui.QFormLayout()
    self.chooseSoundDirectoryButton = QtGui.QPushButton( self.tr(text), self)
    
    self.soundDirectory = QtGui.QLabel(savedDir)
    soundDirectoryLayout.addRow(self.chooseSoundDirectoryButton,
        self.soundDirectory)
    self.setLayout(soundDirectoryLayout)

    self.chooseSoundDirectoryButton.clicked.connect(
        self.chooseSoundsDirectory)

    self.savedDir = savedDir

  def chooseSoundsDirectory(self):
    filename = QtGui.QFileDialog.getExistingDirectory(self,
        self.tr('Sounds directory'), self.savedDir)

    self.soundDirectory.setText(filename)

  def getDirectory(self):
    return self.soundDirectory.text()

  def setEnabled(self, value):
    self.chooseSoundDirectoryButton.setEnabled(value)
