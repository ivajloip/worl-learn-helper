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

def write_to_file(basedir, filename, data):
  with open(basedir + '/' + filename, 'w') as f:
    f.write(data)

def write_to_epub(basedir, filename, files):
  with zipfile.ZipFile(filename, 'w') as epub:
    for f in files: 
      epub.write(basedir + '/' + f, f)

# Convert a pairs of words with given title to an epub 
def convert(words, title, result_filename, author = 'Unknown', lang = 'en'):
  timestamp = datetime.datetime.now()
  epub_id = str(uuid.uuid4())
  toc_id = str(uuid.uuid4())
  tmp_dir = str(uuid.uuid4())
  os.mkdir(tmp_dir)
  
  entries = ''.join([WORD_TEMPLATE.format(word = _[0], translation = _[1])
    for _ in words])
  content = CONTENT_TEMPLATE.format(title_sort = title, timestamp = timestamp,
      title = title, author = author, lang = lang, id = epub_id)
  html = HTML_TEMPLATE.format(title = title, entries = entries)
  toc = TOC_TEMPLATE.format(id = epub_id, title = title, navigation_id = toc_id)

  write_to_file(tmp_dir, 'content.opf', content)
  write_to_file(tmp_dir, 'toc.ncx', toc)
  write_to_file(tmp_dir, 'words.html', html)
  shutil.copy2(TEMPLATES_DIR + '/mimetype', tmp_dir)
  shutil.copy2(TEMPLATES_DIR + '/stylesheet.css', tmp_dir)
  shutil.copy2(TEMPLATES_DIR + '/page_styles.css', tmp_dir)
  shutil.copytree(TEMPLATES_DIR + '/META-INF', tmp_dir + '/META-INF')

  files = ['content.opf', 'toc.ncx', 'words.html', 'mimetype', 'stylesheet.css',
      'page_styles.css', 'META-INF/container.xml']
  write_to_epub(tmp_dir, result_filename, files)

  shutil.rmtree(tmp_dir)

#convert([('a', 'b')], 'Foo', '/tmp/foo')
