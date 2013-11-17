#!/usr/bin/python3

import sys
import re
from PyQt4 import QtCore, QtGui

class MainWindow(QtGui.QMainWindow):

    def __init__(self, use_local = True):
#       creates the window with the title and icon
        super(MainWindow, self).__init__()
        self.resize(440, 360)
        self.setWindowTitle('Word Learning Helper')

#       creates the menuBar and the menu entries
        menubar = self.menuBar()
        file = menubar.addMenu('&File')

        self.createMenuItem('Open', 'icons/open.png', 'Ctrl+O',
            'Open a CSV', self.open_csv, file)

        self.createMenuItem('Import from html', 'icons/import_html.png',
            'Ctrl+I', 'Import from html file', self.import_html, file)

        self.createMenuItem('Save', 'icons/save.png', 'Ctrl+S',
            'Save as CSV', self.save, file)
        file.addSeparator()
        self.createMenuItem('Exit', 'icons/exit.png', 'Ctrl+Q',
            'Exit application', QtCore.SLOT('close()'), file)

#        edit = menubar.addMenu('&Edit')
#        print(dir(self.translation))
#        self.createMenuItem('Copy', 'icons/copy.png', 'Ctrl+C', 'Copy selected text', lambda : self.emit(QtCore.SIGNAL('copy()')), edit)

        scrollableArea = QtGui.QScrollArea(self)
        self.setCentralWidget(scrollableArea)
        frame = QtGui.QFrame()
        scrollableArea.setWidget(frame)

        layout = QtGui.QFormLayout()
        frame.setLayout(layout)
        layout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)

        layout.addRow(self.tr('Francais'), QtGui.QLabel('Bulgare'))
        self.createInputBoxes(layout, 100)

#       connects signal with their handlers
        #self.connect(self.definition, QtCore.SIGNAL('currentChanged(QString)'), self.update_definition) 
        #self.connect(self.translation, QtCore.SIGNAL('currentChanged(QString)'), self.update_translation)
        #self.connect(self.buttonGo, QtCore.SIGNAL('clicked()'), self.look_for_word)
        #self.connect(self.entry, QtCore.SIGNAL('returnPressed()'),self.look_for_word) 

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

    def save(self):
      result = []
      for words in self.input_boxes:
        if words[0].text() == '' or words[1].text() == '':
          break
        else:
          result.append('"{word1}", "{word2}"\n'.format(word1 = words[0].text(),
            word2 = words[1].text()))

      filename = QtGui.QFileDialog.getSaveFileName(self, self.tr("Save file"),
          "", "Files (*.*)")
      
      if filename == '': 
        return

      with open(filename, 'w') as f:
        f.writelines(result)

      print("Successfully wrote words to {0}".format(filename))



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    window = MainWindow()
    sys.exit(app.exec_())       
