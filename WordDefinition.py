from PyQt4 import QtCore, QtGui

class WordDefinition(QtGui.QWidget):
  deleteClicked = QtCore.pyqtSignal()

  def __init__(self, parent = None):
    super(WordDefinition, self).__init__(parent)

    layout = QtGui.QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(5)
    self.setLayout(layout)

    self.word = QtGui.QLineEdit(self)
    self.word.setMinimumWidth(200)
    self.translation = QtGui.QLineEdit(self)
    self.translation.setMinimumWidth(200)
    self.delete_button = QtGui.QPushButton(self.tr("Delete"), self)

    layout.addWidget(self.word)
    layout.addWidget(self.translation)
    layout.addWidget(self.delete_button)

    self.delete_button.clicked.connect(self._deleteClicked)

  def _deleteClicked(self):
    self.deleteClicked.emit()

  def getWord(self):
    return self.word.text()

  def setWord(self, text):
    return self.word.setText(text)

  def getTranslation(self):
    return self.translation.text()

  def setTranslation(self, text):
    return self.translation.setText(text)

