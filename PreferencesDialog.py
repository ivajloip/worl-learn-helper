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
      with open(path) as f:
        conf_as_dict = json.load(f)
    else:
      conf_as_dict = {'config_file_path': CONFIG_FILE_PATH,
          'sound_directory': ''}

    self.config_file_path = conf_as_dict['config_file_path']
    self.sound_directory = conf_as_dict['sound_directory']

  def to_dict(self):
    return {'config_file_path': self.config_file_path,
      'sound_directory': self.sound_directory}

  def write(self, path = None):
    if path == None:
      path = self.config_file_path

    path_dir = os.path.dirname(path)
    if not os.path.exists(path_dir):
      os.makedirs(path_dir)

    with open(path, 'w') as f:
      json.dump(self.to_dict(), f, indent=4, separators=(',', ': '))

    print("Configuration writing finished")

class PreferencesDialog(QtGui.QDialog):

  def __init__(self, configuration, parent = None, config_file = CONFIG_FILE_PATH):
    super(PreferencesDialog, self).__init__(parent)
    self.setWindowTitle(self.tr('Preferences'))

    self.layout = QtGui.QFormLayout()
    self.sound_directory_widget = FileSelector.FileSelector(
        self.tr("Choose..."), configuration.sound_directory, self)
    self.layout.addRow(self.tr("Sound Directory"), self.sound_directory_widget)

    self.setLayout(self.layout)

    ok_button = QtGui.QPushButton(self.tr('&Ok'), self)
    close_button = QtGui.QPushButton(self.tr('&Close'), self)
    self.layout.addRow(close_button, ok_button)

    ok_button.clicked.connect(self.ok_button_clicked)
    close_button.clicked.connect(self.close_button_clicked)

    self.configuration = configuration

  def ok_button_clicked(self):
    self.configuration.write()
    
    self.accept()

  def close_button_clicked(self):
    self.reject()
