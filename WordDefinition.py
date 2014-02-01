from PyQt4 import QtCore, QtGui

class WordDefinition(QtGui.QWidget):
  deleteClicked = QtCore.pyqtSignal()
  moveUp = QtCore.pyqtSignal()
  moveDown = QtCore.pyqtSignal()

  def __init__(self, moveUpEnabled, moveDownEnabled, parent = None):
    super(WordDefinition, self).__init__(parent)

    layout = QtGui.QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(5)
    self.setLayout(layout)

    self.word = QtGui.QLineEdit(self)
    self.word.setMinimumWidth(200)
    self.translation = QtGui.QLineEdit(self)
    self.translation.setMinimumWidth(200)
    self.deleteButton = QtGui.QPushButton(self)
    self.deleteButton.setIcon(QtGui.QIcon('icons/delete.png'))
    self.moveUpButton = QtGui.QPushButton(self)
    self.moveUpButton.setIcon(QtGui.QIcon('icons/up.jpg'))
    self.moveUpButton.setEnabled(moveUpEnabled)
    self.moveDownButton = QtGui.QPushButton(self)
    self.moveDownButton.setIcon(QtGui.QIcon('icons/down.jpg'))
    self.moveDownButton.setEnabled(moveDownEnabled)

    layout.addWidget(self.word)
    layout.addWidget(self.translation)
    layout.addWidget(self.deleteButton)
    layout.addWidget(self.moveUpButton)
    layout.addWidget(self.moveDownButton)

    self.deleteButton.clicked.connect(self._deleteClicked)
    self.moveUpButton.clicked.connect(self._moveUpClicked)
    self.moveDownButton.clicked.connect(self._moveDownClicked)

  def _deleteClicked(self):
    self.deleteClicked.emit()

  def _moveUpClicked(self):
    self.moveUp.emit()

  def _moveDownClicked(self):
    self.moveDown.emit()

  def getWord(self):
    return self.word.text()

  def setWord(self, text):
    return self.word.setText(text)

  def getTranslation(self):
    return self.translation.text()

  def setTranslation(self, text):
    return self.translation.setText(text)

