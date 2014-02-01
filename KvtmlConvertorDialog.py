import time
import os
import re
import FileSelector

from PyQt4 import QtCore, QtGui

# Templates part
TEMPLATE_SOUND = '\n        <sound>file://{sound}</sound>'

TEMPLATE_KVTML_ENTRY = """    <entry id="{index}">
      <translation id="0">{sound1}
        <text>{word}</text>
      </translation>
      <translation id="1">
        <text>{translation}</text>
      </translation>
    </entry>"""

TEMPLATE_KVTML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE kvtml PUBLIC "kvtml2.dtd" "http://edu.kde.org/kvtml/kvtml2.dtd">
<kvtml version="2.0">
  <information>
    <generator>kwordquiz 0.9.2</generator>
    <title>{title}</title>
    <date>{date}</date>
  </information>
  <identifiers>
    <identifier id="0">
      <name>Column 1</name>
      <locale>en</locale>
    </identifier>
    <identifier id="1">
      <name>Column 2</name>
      <locale>en</locale>
    </identifier>
  </identifiers>
  <entries>
{entries}
  </entries>
</kvtml>
"""
# end of teplates


class KvtmlConvertorDialog(QtGui.QDialog):
  def __init__(self, words, configuration, parent=None):
    super(KvtmlConvertorDialog, self).__init__(parent)
    self.words = words

    self.useSoundCheckbox = QtGui.QCheckBox(self)
    self.useSoundCheckbox.setChecked(True)
    self.layout = QtGui.QFormLayout()
    self.layout.addRow(self.tr('Sound'), self.useSoundCheckbox)

    self.soundDirectoryWidget = FileSelector.FileSelector(
        self.tr('Choose...'), configuration.soundDirectory, self)

    self.layout.addRow(self.tr("Sound Directory"), self.soundDirectoryWidget)

    self.titleInput = QtGui.QLineEdit(self)
    self.layout.addRow(self.tr('Title'), self.titleInput)

    self.useSoundCheckbox.stateChanged.connect(self.useSoundStateChange)
    self.finishButton = QtGui.QPushButton(self.tr('Finish'), self)
    self.finishButton.setEnabled(
        self.soundDirectoryWidget.getDirectory() != '')
    self.finishButton.clicked.connect(self.finishButtonClicked)

    self.layout.addRow(self.tr(''), self.finishButton)
    self.setLayout(self.layout)

  def useSoundStateChange(self):
    state = self.useSoundCheckbox.isChecked()

    soundDirectoryPath = self.soundDirectoryWidget.getDirectory()

    self.finishButton.setEnabled(not(state) or soundDirectoryPath != '')

  def finishButtonClicked(self): 
    resultFilename = QtGui.QFileDialog.getSaveFileName(self,
        self.tr('Save file'), '', 'Kvtml files (*.kvtml)')

    if resultFilename == '':
      return

    frenchAudio = self.mapAudioFiles()

    wordsData = [(self.words[index][0], self.words[index][1],
      frenchAudio[index], index) for index in range(len(self.words))]

    title = self.titleInput.text()

    self.writeToKvtml(wordsData, resultFilename, title)

    QtGui.QMessageBox.information(self, self.tr("Export successful"),
        self.tr("The words were successfully saved to {0}").format(
          resultFilename))
    self.accept()

  def hasCommonWord(self, phrase, audio):
    skipWords = ['une', 'un', 'le', 'la', 'les', 'de', 'des', 'du', 'se', 'e',
        'à', 'et', 'ou']
    return any([_ not in skipWords and audio.find(_) >= 0
      for _ in phrase.split(' ')])

  def searchForAudio(self):
    return self.useSoundCheckbox.isChecked()

  def findAudioFile(self, phrase, files, extension = '.flac'):
    if not self.searchForAudio():
      return None

    basedir = self.soundDirectoryWidget.getDirectory() + '/'
    phrase = phrase.lower()
    completeMatch = [_ for _ in files if _ == phrase + extension]

    if len(completeMatch) > 0: 
      print("Found complete match for {0}".format(phrase))
      return basedir + completeMatch[0]

    partialMatch = files

    # sometimes some small words attached to bigger ones can prevent the bigger
    # ones from being recongnized
    phrase = re.sub('[dls][\'`]', '', phrase)

    for word in phrase.split(' '):
      partialMatch = [_ for _ in partialMatch if _.find(word) >= 0]

    if len(partialMatch) == 0:
      partialMatch = [_ for _ in files if self.hasCommonWord(phrase, _)]

    partialMatch = partialMatch[:10]

    optionsCount = len(partialMatch)
    if optionsCount == 0:
      return None
    elif optionsCount == 1:
      return basedir + partialMatch[0]

    title = self.tr("Select audio file to use")
    label = self.tr("For {0}").format(phrase)
    optionToUse = QtGui.QInputDialog.getItem(self, title, label,
        partialMatch, 0, False)

    if not optionToUse[1]:
      return None

    return basedir + optionToUse[0]

  def mapAudioFiles(self):
    if not self.searchForAudio():
      return [None for _ in self.words]

    files = os.listdir(self.soundDirectoryWidget.getDirectory())

    return [self.findAudioFile(word[0], files) for word in self.words]

  def formatSound(self, soundFile):
    if soundFile == None:
      return ''

    return TEMPLATE_SOUND.format(sound = soundFile)

  def getFormattedDate(self, ):
    now = time.localtime()

    return "{year}-{month}-{day}".format(
        year=now.tm_year, month=now.tm_mon, day=now.tm_mday)

  def writeToFile(self, filename, data):
    with open(filename, 'w') as f:
      f.writelines(data)

  def writeToKvtml(self, wordsList, filename, title):
    entriesStr = "\n".join([TEMPLATE_KVTML_ENTRY.format(
      index=_[3], word=_[0], translation=_[1], sound1=self.formatSound(_[2]))
      for _ in wordsList])

    resultingKvtml = TEMPLATE_KVTML.format(title=title, entries=entriesStr,
        date=self.getFormattedDate())

    self.writeToFile(filename, resultingKvtml)

