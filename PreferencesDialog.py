import json
import os.path
import FileSelector

from PyQt4 import QtCore, QtGui

HOME_DIR = os.path.expanduser("~")
SUB_DIR = "/.word-learn-helper/"
FILE_NAME = "config.json"
CONFIG_FILE_PATH = HOME_DIR + SUB_DIR + FILE_NAME

class Config:
  def __init__(self, path = None):
    if path == None:
      path = CONFIG_FILE_PATH

    self.read(path)

  def read(self, path):
    if os.path.exists(path):
      with open(path, encoding='utf-8') as f:
        confAsDict = json.load(f)
    else:
      confAsDict = {'config_file_path': CONFIG_FILE_PATH,
          'sound_directory': ''}

    self.configFilePath = confAsDict['config_file_path']
    self.soundDirectory = confAsDict['sound_directory']

  def toDict(self):
    return {'config_file_path': self.configFilePath,
      'sound_directory': self.soundDirectory}

  def write(self, path = None):
    if path == None:
      path = self.configFilePath

    pathDir = os.path.dirname(path)
    if not os.path.exists(pathDir):
      os.makedirs(pathDir)

    with open(path, 'w', encoding='utf-8') as f:
      json.dump(self.toDict(), f, indent=4, separators=(',', ': '))

    print("Configuration writing finished")

class PreferencesDialog(QtGui.QDialog):

  def __init__(self, configuration, parent = None, configFile = CONFIG_FILE_PATH):
    super(PreferencesDialog, self).__init__(parent)
    self.setWindowTitle(self.tr('Preferences'))

    self.layout = QtGui.QFormLayout()
    self.soundDirectoryWidget = FileSelector.FileSelector(
        self.tr("Choose..."), configuration.soundDirectory, self)
    self.layout.addRow(self.tr("Sound Directory"), self.soundDirectoryWidget)

    self.setLayout(self.layout)

    okButton = QtGui.QPushButton(self.tr('&Ok'), self)
    closeButton = QtGui.QPushButton(self.tr('&Close'), self)
    self.layout.addRow(closeButton, okButton)

    okButton.clicked.connect(self.okButtonClicked)
    closeButton.clicked.connect(self.closeButtonClicked)

    self.configuration = configuration

  def okButtonClicked(self):
    self.configuration.soundDirectory = (
        self.soundDirectoryWidget.getDirectory())

    self.configuration.write()
    
    self.accept()

  def closeButtonClicked(self):
    self.reject()
