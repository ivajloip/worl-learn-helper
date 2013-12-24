from PyQt4 import QtCore, QtGui

class FileSelector(QtGui.QWidget):
  def __init__(self, text, saved_dir = "", parent = None):
    super(FileSelector, self).__init__(parent)

    sound_directory_layout = QtGui.QFormLayout()
    self.choose_sound_directory_button = QtGui.QPushButton( self.tr(text), self)
    
    self.sound_directory = QtGui.QLabel(saved_dir)
    sound_directory_layout.addRow(self.choose_sound_directory_button,
        self.sound_directory)
    self.setLayout(sound_directory_layout)

    self.choose_sound_directory_button.clicked.connect(
        self.choose_sounds_directory)

    self.saved_dir = saved_dir

  def choose_sounds_directory(self):
    filename = QtGui.QFileDialog.getExistingDirectory(self,
        self.tr("Sounds directory"), self.saved_dir)

    self.sound_directory.setText(filename)

  def get_directory(self):
    return self.sound_directory.text()

  def setEnabled(self, value):
    self.choose_sound_directory_button.setEnabled(value)
