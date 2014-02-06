import datetime
import os
import uuid
import shutil
import zipfile

TEMPLATES_DIR = 'epub'

def read_template(filename):
  with open(filename) as f:
    template = f.read()

  return template

HTML_TEMPLATE = read_template(TEMPLATES_DIR + '/words.html')
WORD_TEMPLATE = read_template(TEMPLATES_DIR + '/word_entry.template')
TOC_TEMPLATE = read_template(TEMPLATES_DIR + '/toc.ncx')
CONTENT_TEMPLATE = read_template(TEMPLATES_DIR + '/content.opf')

def writeToFile(basedir, filename, data):
  with open(basedir + '/' + filename, 'w', encoding='utf-8') as f:
    f.write(data)

def writeToEpub(basedir, filename, files):
  with zipfile.ZipFile(filename, 'w') as epub:
    for f in files: 
      epub.write(basedir + '/' + f, f)

# Convert a pairs of words with given title to an epub 
def convert(words, title, resultFilename, author = 'Unknown', lang = 'en'):
  timestamp = datetime.datetime.now()
  epubId = str(uuid.uuid4())
  tocId = str(uuid.uuid4())
  tmpDir = str(uuid.uuid4())
  os.mkdir(tmpDir)
  
  entries = ''.join([WORD_TEMPLATE.format(word = _[0], translation = _[1])
    for _ in words])
  content = CONTENT_TEMPLATE.format(title_sort = title, timestamp = timestamp,
      title = title, author = author, lang = lang, id = epubId)
  html = HTML_TEMPLATE.format(title = title, entries = entries)
  toc = TOC_TEMPLATE.format(id = epubId, title = title, navigation_id = tocId)

  writeToFile(tmpDir, 'content.opf', content)
  writeToFile(tmpDir, 'toc.ncx', toc)
  writeToFile(tmpDir, 'words.html', html)
  shutil.copy2(TEMPLATES_DIR + '/mimetype', tmpDir)
  shutil.copy2(TEMPLATES_DIR + '/stylesheet.css', tmpDir)
  shutil.copy2(TEMPLATES_DIR + '/page_styles.css', tmpDir)
  shutil.copytree(TEMPLATES_DIR + '/META-INF', tmpDir + '/META-INF')

  files = ['content.opf', 'toc.ncx', 'words.html', 'mimetype', 'stylesheet.css',
      'page_styles.css', 'META-INF/container.xml']
  writeToEpub(tmpDir, resultFilename, files)

  shutil.rmtree(tmpDir)

#convert([('a', 'b')], 'Foo', '/tmp/foo')
