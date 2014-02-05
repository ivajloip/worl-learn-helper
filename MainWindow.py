#!/usr/bin/python3

import sys
import re
import time
import os
import urllib.request
import uuid
import zipfile
import functools
import epub_converter
import KvtmlConvertorDialog
import AboutDialog
import PreferencesDialog
import WordDefinition
import odt_parser
import docx_parser

from PyQt4 import QtCore, QtGui

STATUS_BAR_TIMEOUT = 10000
MAX_WORD_COUNT = 100

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
    </table>
  </body>

</html>
"""
# end of teplates


class MainWindow(QtGui.QMainWindow):

  def __init__(self, use_local = True):
#       creates the window with the title and icon
    super(MainWindow, self).__init__()
    self.resize(450, 360)
    self.setWindowTitle(self.tr('Word Learning Helper'))
    self.statusBar()

    self.pool = QtCore.QThreadPool()
    self.pool.setMaxThreadCount(5)

    self._createMenuBar()
    
    scrollableArea = QtGui.QScrollArea(self)
    self.setCentralWidget(scrollableArea)
    frame = QtGui.QFrame()
    scrollableArea.setWidget(frame)

    layout = QtGui.QVBoxLayout()
    frame.setLayout(layout)
    layout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)

    self._createTableTitle(layout)
    self._createInputBoxes(layout, MAX_WORD_COUNT)

    self.center()
    self.show()

    self.configuration = PreferencesDialog.Config()

  def _createTableTitle(self, layout):
    titleWidget = QtGui.QWidget(self)
    titleLayout = QtGui.QHBoxLayout()
    titleLayout.setContentsMargins(0, 0, 0, 0)
    titleLayout.setSpacing(5)

    titleWidget.setLayout(titleLayout)

    frLabel = QtGui.QLabel(self.tr('Francais'))
    frLabel.setMinimumWidth(200)
    bgLabel = QtGui.QLabel(self.tr('Bulgare'))
    bgLabel.setMinimumWidth(200)
    titleLayout.addWidget(frLabel)
    titleLayout.addWidget(bgLabel)

    layout.addWidget(titleWidget)

  def _createMenuItem(self, label, iconLocation, shortCut, statusTip, func, addTo):
    newActoin = QtGui.QAction(QtGui.QIcon(iconLocation), self.tr(label), self)
    newActoin.setShortcut(shortCut)
    newActoin.setStatusTip(self.tr(statusTip))
    self.connect(newActoin, QtCore.SIGNAL('triggered()'), func)
    addTo.addAction(newActoin)       

  def _createMenuBar(self):
    menubar = self.menuBar()
    fileMenu = menubar.addMenu('&File')

    self._createMenuItem('Open', 'icons/open.png', 'Ctrl+O',
        'Open csv, html, odt or docx file', self._open, fileMenu)

    self._createMenuItem('Save', 'icons/save.png', 'Ctrl+S',
        'Save as CSV', self.save, fileMenu)

    export = fileMenu.addMenu('&Export')
    self._createMenuItem('Export to kvtml', 'icons/export_kvtml.png',
        'Ctrl+K', 'Export to wordquiz/kwordquiz file', self.exportKvtml,
        export)

    self._createMenuItem('Export to html', 'icons/export_html.png',
        'Ctrl+H', 'Export to html file', self.exportHtml, export)
    self._createMenuItem('Export to epub', 'icons/export_epub.png',
        'Ctrl+E', 'Export to epub file', self.exportEpub, export)

    fileMenu.addSeparator()
    self._createMenuItem('Exit', 'icons/exit.png', 'Ctrl+Q',
        'Exit application', QtCore.SLOT('close()'), fileMenu)

    tools = menubar.addMenu('&Tools')
    self._createMenuItem('Download audio files', 'icons/download_audios.png',
        'Ctrl+D', 'Download free audio files', self.downloadAudios,
        tools)

    self._createMenuItem('Download audio files from url',
        'icons/download_audios.png', 'Ctrl+C',
        'Download free audio files from other url',
        self.downloadAudiosCustomUrl, tools)

    self._createMenuItem('Preferences', 'icons/preferences.png',
        'Ctrl+P', 'Program configuration', self.showPreferencesDialog, tools)

    helpSubmenu = menubar.addMenu('&Help')

    self._createMenuItem('About',
        'icons/about.png', 'Ctrl+L',
        'Provides license and additional information',
        self.showAboutDialog, helpSubmenu)

  def center(self):
    screen = QtGui.QDesktopWidget().screenGeometry()
    size =  self.geometry()
    self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)  

  def createInputBox(self, layout, moveUpEnabled, moveDownEnabled):
    newWordDefinition = WordDefinition.WordDefinition(moveUpEnabled,
        moveDownEnabled, self)
    layout.addWidget(newWordDefinition)

    return newWordDefinition

  def _swapWords(self, firstWordIndex, secondWordIndex):
    words = self._getWords()

    tmp = words[firstWordIndex]
    words[firstWordIndex] = words[secondWordIndex]
    words[secondWordIndex] = tmp

    self._updateWordPairs(words, firstWordIndex, secondWordIndex + 1)

  def _deleteWord(self, number):
    words = self._getWords()
    newWords = words[:number] + words[number + 1:]
    self._updateWordPairs(newWords, number, len(words))

  def _createInputBoxes(self, layout, count):
    self.inputBoxes = []
    for _ in range(count):
      inputBox = self.createInputBox(layout, _ != 0, _ != count - 1)
      self.inputBoxes.append(inputBox)

      inputBox.deleteClicked.connect(functools.partial(self._deleteWord, _))
      inputBox.moveUp.connect(functools.partial(self._swapWords, _ - 1, _))
      inputBox.moveDown.connect(functools.partial(self._swapWords, _, _ + 1))

  def parseCsv(self, filename):
    with open(filename) as fin:
      lines = fin.readlines()

    wordPairs = [line[1:-2].split('", "') for line in lines]

    return wordPairs

  def parseHtml(self, filename):
    with open(filename) as f:
      lines = f.readlines()

    lines = lines[17:-3]

    frenchWords = [re.sub('\s*<td>(.*)</td>\s*$', '\\1', _)
        for _ in lines[1::4]]
    bulgarianWords = [re.sub('\s*<td>(.*)</td>\s*$', '\\1', _)
        for _ in lines[2::4]]

    return list(zip(frenchWords, bulgarianWords))

  def _open(self):
    parsers = {self.tr("Html files (*.html *.xhtml)"): self.parseHtml,
        self.tr("Odt files (*.odt)"): odt_parser.parseOdt,
        self.tr("Csv files (*.csv)"): self.parseCsv,
        self.tr("Docx files (*.docx)"): docx_parser.parseDocx}

    filters = list(parsers.keys())
    filters.sort()

    filename, fileFilter = QtGui.QFileDialog.getOpenFileNameAndFilter(self,
        self.tr("Import from file"), "",
        ";;".join(filters))

    if filename == '': 
      return

    parser = parsers[fileFilter]
    wordPairs = list(parser(filename))

    self._updateWordPairs(wordPairs)

  def _updateWordPairs(self, wordPairs, begin=0, end=MAX_WORD_COUNT):
    for index in range(begin, len(wordPairs)):
      self.inputBoxes[index].setWord(wordPairs[index][0])
      self.inputBoxes[index].setTranslation(wordPairs[index][1])

    for index in range(max(begin, len(wordPairs)), end):
      self.inputBoxes[index].setWord('')
      self.inputBoxes[index].setTranslation('')

  def _getWords(self):
    return [(words.getWord(), words.getTranslation()) 
        for words in self.inputBoxes
        if words.getWord() != '' or words.getTranslation() != '']

  def exportKvtml(self):
    words = self._getWords()
    converterDialog = KvtmlConvertorDialog.KvtmlConvertorDialog(words,
        self.configuration, self)
    converterDialog.exec_()

  def exportHtml(self):
    filename = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save file"),
        "", self.tr("Html files (*.html)"))

    if filename == '':
      return

    title, _ = QtGui.QInputDialog.getText(self, self.tr("Title"), self.tr(
      "Title of the html file"))

    wordsList = self._getWords()

    entriesStr = "\n".join([TEMPLATE_HTML_ROW.format(
      word=_[0], translation=_[1]) for _ in wordsList])

    resultingHtml = TEMPLATE_HTML.format(title=title, entries=entriesStr)

    with open(filename, 'w') as f:
      f.writelines(resultingHtml)

    self.statusBar().showMessage(self.tr("Exported successfully to {0}").format(
      filename), STATUS_BAR_TIMEOUT)

  def exportEpub(self):
    filename = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save file"),
        "", self.tr("Epub files (*.epub)"))

    if filename == '':
      return

    title, _ = QtGui.QInputDialog.getText(self, self.tr("Title"), self.tr(
      "Title of the epub file"))

    wordsList = self._getWords()
    epub_converter.convert(wordsList, title, filename)

    self.statusBar().showMessage(self.tr("Exported successfully to {0}").format(
      filename), STATUS_BAR_TIMEOUT)

  def save(self):
    words = self._getWords()
    result = [TEMPLATE_CSV.format(word1 = word, word2 = translation) 
      for word, translation in words]

    filename = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save file"),
        "", self.tr("Comma separated values files (*.csv)"))
    
    if filename == '': 
      return

    with open(filename, 'w') as f:
      f.writelines(result)

    print("Successfully wrote words to {0}".format(filename))

  def showAboutDialog(self):
    with open('LICENSE', 'r') as f:
      license = f.read()
    aboutDialog = AboutDialog.AboutDialog(license, self)
    aboutDialog.exec_()

  def showPreferencesDialog(self):
    preferencesDialog = PreferencesDialog.PreferencesDialog(self.configuration,
        self, "")
    preferencesDialog.exec_()

  def downloadAudios(self,
      url = 'http://ubuntuone.com/30FlazWAzqPCmlebqNwiXZ'): 
    dirname = QtGui.QFileDialog.getExistingDirectory(self,
        self.tr("Directory for the sounds"))
    
    if dirname == '': 
      return

    resultFilename = "{0}/{1}.zip".format(dirname, uuid.uuid4().hex)

    self.statusBar().showMessage(self.tr("Connecting to the server"))
    zipFileDownloader = ZipFileDownloader(url, dirname)
    zipFileDownloader.executionStatus.newValue.connect(
        self.updateStatusBarWithTimeout)

    self.pool.start(zipFileDownloader)

  @QtCore.pyqtSlot(str, int)
  def updateStatusBarWithTimeout(self, message, timeout=0):
    self.statusBar().showMessage(message)

  def downloadAudiosCustomUrl(self):
    url = QtGui.QInputDialog.getText(self, self.tr("Url"),
        self.tr("The url to use for audio files"))

    if url == '':
      QtGui.QMessageBox(self.tr("Aborting as no url was provided"))

    self.downloadAudios(url)

class ExecutionStatus(QtCore.QObject):
  newValue = QtCore.pyqtSignal(str, int)

class ZipFileDownloader(QtCore.QRunnable):

  def __init__(self, url, dirname, parent=None):
    super(ZipFileDownloader, self).__init__()
    self.executionStatus = ExecutionStatus()
    self.url = url
    self.dirname = dirname

  def run(self): 
    resultFilename = "{0}/{1}.zip".format(self.dirname, uuid.uuid4().hex)
    self._downloadFile(self.url, resultFilename)
    self._unpackFileToDir(resultFilename)

  def _tr(self, text):
    return QtCore.QCoreApplication.translate("ZipFileDownloader", text)

  def _downloadFile(self, url, resultFilename):
    readSize = 65507

    with urllib.request.urlopen(url) as webFile:
      fileSize = int(webFile.info()['Content-Length'])
      downloaded = 0
      with open(resultFilename, 'wb') as fout:
        while(True):
          buf = webFile.read(readSize)
          if not buf:
            break

          fout.write(buf)
          downloaded += len(buf)

          self.executionStatus.newValue.emit(
              self._tr("Downloaded {} KB of {} KB".format(downloaded // 1024,
                  fileSize // 1024)), 0)

    self.executionStatus.newValue.emit(self._tr("Download completed"),
        STATUS_BAR_TIMEOUT)

  def _unpackFileToDir(self, resultFilename):
    self.executionStatus.newValue.emit(
        self._tr("Unpacking files, please wait"), 0)

    with zipfile.ZipFile(resultFilename) as zf:
      zf.extractall(self.dirname)

    self.executionStatus.newValue.emit(self._tr("Unpacking finished"),
        STATUS_BAR_TIMEOUT)

