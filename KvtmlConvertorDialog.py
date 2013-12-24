import time
import os
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

    self.use_sound_checkbox = QtGui.QCheckBox(self)
    self.use_sound_checkbox.setChecked(True)
    self.layout = QtGui.QFormLayout()
    self.layout.addRow(self.tr("Sound"), self.use_sound_checkbox)

    self.sound_directory_widget = FileSelector.FileSelector(
        self.tr("Choose..."), configuration.sound_directory, self)

    self.layout.addRow(self.tr("Sound Directory"), self.sound_directory_widget)

    self.title_input = QtGui.QLineEdit(self)
    self.layout.addRow(self.tr("Title"), self.title_input)

    self.use_sound_checkbox.stateChanged.connect(self.use_sound_state_change)
    self.finish_button = QtGui.QPushButton(self.tr("Finish"), self)
    self.finish_button.setEnabled(
        self.sound_directory_widget.get_directory() != '')
    self.finish_button.clicked.connect(self.finish_button_clicked)

    self.layout.addRow(self.tr(""), self.finish_button)
    self.setLayout(self.layout)

  def use_sound_state_change(self):
    state = self.use_sound_checkbox.isChecked()
    self.choose_sound_directory_button.setEnabled(state)

    sound_directory_path = self.sound_directory_widget.get_directory()

    self.finish_button.setEnabled(not(state) or sound_directory_path != '')

  def finish_button_clicked(self): 
    result_filename = QtGui.QFileDialog.getSaveFileName(self,
        self.tr("Save file"), "", "Kvtml files (*.kvtml)")

    if result_filename == '':
      return

    french_audio = self.map_audio_files()

    words_data = [(self.words[index][0], self.words[index][1],
      french_audio[index], index) for index in range(len(self.words))]

    title = self.title_input.text()

    self.write_to_kvtml(words_data, result_filename, title)

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
    if not self.use_sound_checkbox.isChecked():
      return None

    basedir = self.sound_directory_widget.get_directory() + '/'
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
    files = os.listdir(self.sound_directory_widget.get_directory())

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
    entries_str = "\n".join([TEMPLATE_KVTML_ENTRY.format(
      index=_[3], word=_[0], translation=_[1], sound1=self.format_sound(_[2]))
      for _ in words_list])

    resulting_kvtml = TEMPLATE_KVTML.format(title=title, entries=entries_str,
        date=self.get_formatted_date())

    self.write_to_file(filename, resulting_kvtml)

