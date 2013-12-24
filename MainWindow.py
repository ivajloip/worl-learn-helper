#!/usr/bin/python3

import sys
import re
import time
import os
import urllib.request
import uuid
import zipfile
import epub_converter
import KvtmlConvertorDialog
import AboutDialog
import PreferencesDialog

from PyQt4 import QtCore, QtGui

STATUS_BAR_TIMEOUT = 10000

# Templates part
TEMPLATE_CSV = '"{word1}", "{word2}"\n'

TEMPLATE_HTML_ROW = """      <tr>
        <td>{word}</td>
        <td>{translation}</td>
      </tr>"""

TEMPLATE_HTML = """<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>{title}</title>
    <style type="text/css">
      td {{padding-left: 1em;}}
      th {{padding-left: 1em;}}
    </style>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
  </head>
  <body style="width:100%">
    <h1 style="text-align:center; width:90%;">{title}</h1>
    <table style="width:90%; border-collapse:collapse;" border="1">
      <tr>
        <th style="text-align:left; width:49%;">français</th>
        <th style="text-align:left; width:49%;">bulgare</th>
      </tr>
{entries}
  </body>

</html>
"""
# end of teplates


class MainWindow(QtGui.QMainWindow):

  def __init__(self, use_local = True):
#       creates the window with the title and icon
    super(MainWindow, self).__init__()
    self.resize(450, 360)
    self.setWindowTitle('Word Learning Helper')
    self.statusBar()

    self.pool = QtCore.QThreadPool()
    self.pool.setMaxThreadCount(5)

#       creates the menuBar and the menu entries
    menubar = self.menuBar()
    file_menu = menubar.addMenu('&File')

    self.createMenuItem('Open', 'icons/open.png', 'Ctrl+O',
        'Open a CSV', self.open_csv, file_menu)

    self.createMenuItem('Import from html', 'icons/import_html.png',
        'Ctrl+I', 'Import from html file', self.import_html, file_menu)

    self.createMenuItem('Save', 'icons/save.png', 'Ctrl+S',
        'Save as CSV', self.save, file_menu)

    export = file_menu.addMenu('&Export')
    self.createMenuItem('Export to kvtml', 'icons/export_kvtml.png',
        'Ctrl+K', 'Export to wordquiz/kwordquiz file', self.export_kvtml,
        export)

    self.createMenuItem('Export to html', 'icons/export_html.png',
        'Ctrl+H', 'Export to html file', self.export_html, export)
    self.createMenuItem('Export to epub', 'icons/export_epub.png',
        'Ctrl+E', 'Export to epub file', self.export_epub, export)

    file_menu.addSeparator()
    self.createMenuItem('Exit', 'icons/exit.png', 'Ctrl+Q',
        'Exit application', QtCore.SLOT('close()'), file_menu)

    tools = menubar.addMenu('&Tools')
    self.createMenuItem('Download audio files', 'icons/download_audios.png',
        'Ctrl+D', 'Download free audio files', self.download_audios,
        tools)

    self.createMenuItem('Download audio files from url',
        'icons/download_audios.png', 'Ctrl+C',
        'Download free audio files from other url',
        self.download_audios_custom_url, tools)

    self.createMenuItem('Preferences', 'icons/preferences.png',
        'Ctrl+P', 'Program configuration', self.show_preferences_dialog, tools)

    help_submenu = menubar.addMenu('&Help')

    self.createMenuItem('About',
        'icons/about.png', 'Ctrl+L',
        'Provides license and additional information',
        self.show_about_dialog, help_submenu)
    
    scrollableArea = QtGui.QScrollArea(self)
    self.setCentralWidget(scrollableArea)
    frame = QtGui.QFrame()
    scrollableArea.setWidget(frame)

    layout = QtGui.QFormLayout()
    frame.setLayout(layout)
    layout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)

    layout.addRow(self.tr('Francais'), QtGui.QLabel('Bulgare'))
    self.createInputBoxes(layout, 100)

    self.center()
    self.show()

    self.configuration = PreferencesDialog.Config()

  def createMenuItem(self, label, iconLocation, shortCut, statusTip, func, addTo):
    tmp = QtGui.QAction(QtGui.QIcon(iconLocation), label, self)
    tmp.setShortcut(shortCut)
    tmp.setStatusTip(statusTip)
    self.connect(tmp, QtCore.SIGNAL('triggered()'), func)
    addTo.addAction(tmp)       

  def center(self):
    screen = QtGui.QDesktopWidget().screenGeometry()
    size =  self.geometry()
    self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)  

  def createInputBox(self, layout):
    word1 = QtGui.QLineEdit(self)
    word1.setMinimumWidth(200)
    word2 = QtGui.QLineEdit(self)
    word2.setMinimumWidth(200)
    layout.addRow(word1, word2)

    return (word1, word2)

  def createInputBoxes(self, layout, count):
    self.input_boxes = []
    for _ in range(count):
      input_box = self.createInputBox(layout)
      self.input_boxes.append(input_box)

  def open_csv(self):
    filename = QtGui.QFileDialog.getOpenFileName(self, self.tr("Open file"),
        "", "All files (*.*)")

    if filename == '': 
      return

    with open(filename) as fin:
      lines = fin.readlines()

    for index in range(len(lines)):
      word1, word2 = lines[index][1:-2].split('", "')
      self.input_boxes[index][0].setText(word1)
      self.input_boxes[index][1].setText(word2)

  def parse_html(self, filename):
    with open(filename) as f:
      lines = f.readlines()

    lines = lines[17:-3]

    french_words = [re.sub('\s*<td>(.*)</td>\s*$', '\\1', _)
        for _ in lines[1::4]]
    bulgarian_words = [re.sub('\s*<td>(.*)</td>\s*$', '\\1', _)
        for _ in lines[2::4]]

    return list(zip(french_words, bulgarian_words))

  def import_html(self):
    filename = QtGui.QFileDialog.getOpenFileName(self,
        self.tr("Import from html file"), "", "Html files (*.html *.xhtml)")

    if filename == '': 
      return

    word_pairs = self.parse_html(filename)

    for index in range(len(word_pairs)):
      self.input_boxes[index][0].setText(word_pairs[index][0])
      self.input_boxes[index][1].setText(word_pairs[index][1])

  def _get_words(self):
    return [(words[0].text(), words[1].text()) 
        for words in self.input_boxes
        if words[0].text() != '' and words[1].text != '']

  def export_kvtml(self):
    words = self._get_words()
    converterDialog = KvtmlConvertorDialog.KvtmlConvertorDialog(words,
        self.configuration, self)
    converterDialog.exec_()

  def export_html(self):
    filename = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save file"),
        "", "Html files (*.html)")

    title, _ = QtGui.QInputDialog.getText(self, self.tr("Title"), self.tr(
      "Title of the html file"))

    words_list = self._get_words()

    entries_str = "\n".join([TEMPLATE_HTML_ROW.format(
      word=_[0], translation=_[1]) for _ in words_list])

    resulting_html = TEMPLATE_HTML.format(title=title, entries=entries_str)

    with open(filename, 'w') as f:
      f.writelines(resulting_html)

    self.statusBar().showMessage(self.tr("Exported successfully to {0}").format(
      filename), STATUS_BAR_TIMEOUT)

  def export_epub(self):
    filename = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save file"),
        "", "Epub files (*.epub)")

    title, _ = QtGui.QInputDialog.getText(self, self.tr("Title"), self.tr(
      "Title of the epub file"))

    words_list = self._get_words()
    epub_converter.convert(words_list, title, filename)

    self.statusBar().showMessage(self.tr("Exported successfully to {0}").format(
      filename), STATUS_BAR_TIMEOUT)

  def save(self):
    result = [TEMPLATE_CSV.format(word1 = words[0].text(),
      word2 = words[1].text()) 
      for words in self.input_boxes
      if words[0].text() != '' and words[1].text != '']

    filename = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save file"),
        "", "Comma separated values files (*.csv)")
    
    if filename == '': 
      return

    with open(filename, 'w') as f:
      f.writelines(result)

    print("Successfully wrote words to {0}".format(filename))

  def show_about_dialog(self):
    with open('LICENSE', 'r') as f:
      license = f.read()
    about_dialog = AboutDialog.AboutDialog(license, self)
    about_dialog.exec_()

  def show_preferences_dialog(self):
    preferences_dialog = PreferencesDialog.PreferencesDialog(self.configuration,
        self, "")
    preferences_dialog.exec_()

  def download_audios(self,
      url = 'http://ubuntuone.com/30FlazWAzqPCmlebqNwiXZ'): 
    dirname = QtGui.QFileDialog.getExistingDirectory(self,
        self.tr("Directory for the sounds"))
    
    if dirname == '': 
      return

    result_filename = "{0}/{1}.zip".format(dirname, uuid.uuid4().hex)

    self.statusBar().showMessage(self.tr("Connecting to the server"))
    zipFileDownloader = ZipFileDownloader(url, dirname)
    zipFileDownloader.executionStatus.newValue.connect(
        self.updateStatusBarWithTimeout)

    self.pool.start(zipFileDownloader)

  @QtCore.pyqtSlot(str, int)
  def updateStatusBarWithTimeout(self, message, timeout=0):
    self.statusBar().showMessage(message)

  def download_audios_custom_url(self):
    url = QtGui.QInputDialog.getText(self, self.tr("Url"),
        self.tr("The url to use for audio files"))

    if url == '':
      QtGui.QMessageBox(self.tr("Aborting as no url was provided"))

    self.download_audios(url)

class ExecutionStatus(QtCore.QObject):
  newValue = QtCore.pyqtSignal(str, int)

class ZipFileDownloader(QtCore.QRunnable):

  def __init__(self, url, dirname, parent=None):
    super(ZipFileDownloader, self).__init__()
    self.executionStatus = ExecutionStatus()
    self.url = url
    self.dirname = dirname

  def run(self): 
    result_filename = "{0}/{1}.zip".format(self.dirname, uuid.uuid4().hex)
    self._download_file(self.url, result_filename)
    self._unpack_file_to_dir(result_filename)

  def _tr(self, text):
    return QtCore.QCoreApplication.translate("ZipFileDownloader", text)

  def _download_file(self, url, result_filename):
    read_size = 65507

    with urllib.request.urlopen(url) as web_file:
      file_size = int(web_file.info()['Content-Length'])
      downloaded = 0
      with open(result_filename, 'wb') as fout:
        while(True):
          buf = web_file.read(read_size)
          if not buf:
            break

          fout.write(buf)
          downloaded += len(buf)

          self.executionStatus.newValue.emit(
              self._tr("Downloaded {} KB of {} KB".format(downloaded // 1024,
                  file_size // 1024)), 0)

    self.executionStatus.newValue.emit(self._tr("Download completed"),
        STATUS_BAR_TIMEOUT)

  def _unpack_file_to_dir(self, result_filename):
    self.executionStatus.newValue.emit(
        self._tr("Unpacking files, please wait"), 0)

    with zipfile.ZipFile(result_filename) as zf:
      zf.extractall(self.dirname)

    self.executionStatus.newValue.emit(self._tr("Unpacking finished"),
        STATUS_BAR_TIMEOUT)

