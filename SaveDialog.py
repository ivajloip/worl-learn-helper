import os.path
import re

from PyQt4 import QtCore, QtGui

class SaveDialog(QtGui.QFileDialog):
  def __init__(self, caption="", directory="", fileFilter="", parent=None):
    super(SaveDialog, self).__init__(parent, caption, directory, fileFilter)

    self.setAcceptMode(QtGui.QFileDialog.AcceptSave)
    self.setFileMode(QtGui.QFileDialog.AnyFile)

  def accept(self):
    selectedFiles = self.selectedFiles()
    if len(selectedFiles) == 1:
      if os.path.isdir(selectedFiles[0]):
        return

      filename = self.adjustSelectedFilename(selectedFiles[0])
      yesNoButtons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
      confirmationMessage = "{} already exists.\nDo you want to replace it?"

      if os.path.exists(filename) and QtGui.QMessageBox.warning(self,
          self.windowTitle(),
          self.tr(confirmationMessage).format(filename),
          yesNoButtons, QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
        return

      self.fileSelected.emit(filename)
      self.saveLocation = filename

      QtGui.QDialog.accept(self)
    else:
      self.saveLocation = ''

  def adjustSelectedFilename(self, filename):
    fileFilter = self.selectedNameFilter()
    extension = re.sub('.*\(\*(\..*)\).*', '\\1', fileFilter)

    if not filename.endswith(extension):
      filename += extension

    return filename

  @staticmethod
  def getSaveFileName(parent=None, caption="", directory="", fileFilter=""):
    dialog = SaveDialog(caption, directory, fileFilter, parent)

    if dialog.exec_() == 1:
      selectedFiles = dialog.selectedFiles()

      return dialog.saveLocation

    return ''

