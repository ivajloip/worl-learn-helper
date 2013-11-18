#!/usr/bin/python3

import sys
import re
import time
import os
import urllib.request
import uuid
import zipfile
from PyQt4 import QtCore, QtGui

# Templates part
TEMPLATE_CSV = '"{word1}", "{word2}"\n'

TEMPLATE_SOUND = '\n        <sound>file://{sound}</sound>'

TEMPLATE_ENTRY = """    <entry id="{index}">
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


class MainWindow(QtGui.QMainWindow):

    def __init__(self, use_local = True):
#       creates the window with the title and icon
        super(MainWindow, self).__init__()
        self.resize(440, 360)
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
          "", "Files (*.*)")

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
          self.tr("Import from html file"), "", "Files (*.html *.xhtml)")

      if filename == '': 
        return

      word_pairs = self.parse_html(filename)

      for index in range(len(word_pairs)):
        self.input_boxes[index][0].setText(word_pairs[index][0])
        self.input_boxes[index][1].setText(word_pairs[index][1])

    def export_kvtml(self):
      result = [(words[0].text(), words[1].text()) 
          for words in self.input_boxes
          if words[0].text() != '' and words[1].text != '']
      converterDialog = KvtmlConvertorDialog(result, self)
      converterDialog.exec_()

    def save(self):
      result = [TEMPLATE_CSV.format(word1 = words[0].text(),
        word2 = words[1].text()) 
        for words in self.input_boxes
        if words[0].text() != '' and words[1].text != '']

      filename = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save file"),
          "", "Files (*.*)")
      
      if filename == '': 
        return

      with open(filename, 'w') as f:
        f.writelines(result)

      print("Successfully wrote words to {0}".format(filename))


    def download_audios(self,
        url = 'https://docs.google.com/uc?export=download&id=0B4itASCdgeQKbVdFVVQxeGh6UU0'): 
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

    self.executionStatus.newValue.emit(self._tr("Download completed"), 10000)

  def _unpack_file_to_dir(self, result_filename):
    self.executionStatus.newValue.emit(
        self._tr("Unpacking files, please wait"), 0)

    with zipfile.ZipFile(result_filename) as zf:
      zf.extractall(self.dirname)

    self.executionStatus.newValue.emit(self._tr("Unpacking finished"), 10000)

class KvtmlConvertorDialog(QtGui.QDialog):
  def __init__(self, words, parent=None):
    super(KvtmlConvertorDialog, self).__init__(parent)
    self.words = words

    use_sound_checkbox = QtGui.QCheckBox(self)
    self.layout = QtGui.QFormLayout()
    self.layout.addRow(self.tr("Sound"), use_sound_checkbox)

    sound_directory_widget = QtGui.QWidget(self)
    sound_directory_layout = QtGui.QFormLayout()
    choose_sound_directory_button = QtGui.QPushButton(self.tr("Choose... "),
        self)
    self.sound_directory = QtGui.QLabel("")
    sound_directory_layout.addRow(choose_sound_directory_button, self.sound_directory)
    sound_directory_widget.setLayout(sound_directory_layout)

    self.layout.addRow(self.tr("Sound Directory"), sound_directory_widget)

    self.finish_button = QtGui.QPushButton(self.tr("Finish"), self)
    self.finish_button.setEnabled(False)
    self.finish_button.clicked.connect(self.finish_button_clicked)

    self.layout.addRow(self.tr(""), self.finish_button)
    self.setLayout(self.layout)

    choose_sound_directory_button.clicked.connect(self.choose_sounds_directory)

  def choose_sounds_directory(self):
      filename = QtGui.QFileDialog.getExistingDirectory(self,
          self.tr("Sounds directory"))

      self.sound_directory.setText(filename)

      if filename != '':
        self.finish_button.setEnabled(True)
      else:
        self.finish_button.setEnabled(False)

  def finish_button_clicked(self): 
    result_filename = QtGui.QFileDialog.getSaveFileName(self,
        self.tr("Save file"), "", "Files (*.*)")

    if result_filename == '':
      return

    french_audio = self.map_audio_files()

    words_data = [(self.words[index][0], self.words[index][1],
      french_audio[index], index) for index in range(len(self.words))]

    self.write_to_kvtml(words_data, result_filename, 'title')

    QtGui.QMessageBox.information(self, self.tr("Export successful"),
        self.tr("The words were successfully saved to {0}").format(
          result_filename))
    self.accept()

  def has_common_word(self, phrase, audio):
    skip_words = ['une', 'un', 'le', 'la', 'les', 'de', 'des', 'du', 'se', 'e',
        'à', 'et', 'ou']
    return any([_ not in skip_words and audio.find(_) >= 0
      for _ in phrase.split(' ')])

  def find_audio_file(self, phrase, files, extension = '.flac'):
    basedir = self.sound_directory.text() + '/'
    phrase = phrase.lower()
    complete_match = [_ for _ in files if _ == phrase + extension]

    if len(complete_match) > 0: 
      print("Found complete match for {0}".format(phrase))
      return basedir + complete_match[0]

    partial_match = files
    for word in phrase.split(' '):
      partial_match = [_ for _ in partial_match if _.find(word) >= 0]

    if len(partial_match) == 0:
      partial_match = [_ for _ in files if self.has_common_word(phrase, _)]

    partial_match = partial_match[:10]

    options_count = len(partial_match)
    if options_count == 0:
      return None
    elif options_count == 1:
      return partial_match[0]

    title = self.tr("Select audio file to use")
    label = self.tr("For {0}").format(phrase)
    option_to_use = QtGui.QInputDialog.getItem(self, title, label,
        partial_match, 0, False)

    if not option_to_use[1]:
      return None

    return option_to_use[0]

  def map_audio_files(self):
    files = os.listdir(self.sound_directory.text())

    return [self.find_audio_file(word[0], files) for word in self.words]

  def format_sound(self, sound_file):
    if sound_file == None:
      return ''

    return TEMPLATE_SOUND.format(sound = sound_file)

  def get_formatted_date(self, ):
    now = time.localtime()

    return "{year}-{month}-{day}".format(
        year=now.tm_year, month=now.tm_mon, day=now.tm_mday)

  def write_to_file(self, filename, data):
    with open(filename, 'w') as f:
      f.writelines(data)

  def write_to_kvtml(self, words_list, filename, title):
    entries_str = "\n".join([TEMPLATE_ENTRY.format(
      index=_[3], word=_[0], translation=_[1], sound1=self.format_sound(_[2]))
      for _ in words_list])

    resulting_kvtml = TEMPLATE_KVTML.format(title=title, entries=entries_str,
        date=self.get_formatted_date())

    self.write_to_file(filename, resulting_kvtml)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    window = MainWindow()
    sys.exit(app.exec_())       
