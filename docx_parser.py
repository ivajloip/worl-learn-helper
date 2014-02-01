from lxml import etree
import zipfile
import re

# Taken from https://github.com/mikemaccana/python-docx/blob/master/docx.py
# All Word prefixes / namespace matches used in document.xml & core.xml.
# LXML doesn't actually use prefixes (just the real namespace) , but these
# make it easier to copy Word output more easily.
nsprefixes = {
    'mo': 'http://schemas.microsoft.com/office/mac/office/2008/main',
    'o': 'urn:schemas-microsoft-com:office:office',
    've': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    # Text Content
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w10': 'urn:schemas-microsoft-com:office:word',
    'wne': 'http://schemas.microsoft.com/office/word/2006/wordml',
    # Drawing
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'mv': 'urn:schemas-microsoft-com:mac:vml',
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
    'v': 'urn:schemas-microsoft-com:vml',
    'wp': ('http://schemas.openxmlformats.org/drawingml/2006/wordprocessing'
            'Drawing'),
    # Properties (core and extended)
    'cp': ('http://schemas.openxmlformats.org/package/2006/metadata/core-pr'
            'operties'),
    'dc': 'http://purl.org/dc/elements/1.1/',
    'ep': ('http://schemas.openxmlformats.org/officeDocument/2006/extended-'
            'properties'),
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    # Content Types
    'ct': 'http://schemas.openxmlformats.org/package/2006/content-types',
    # Package Relationships
    'r': ('http://schemas.openxmlformats.org/officeDocument/2006/relationsh'
           'ips'),
    'pr': 'http://schemas.openxmlformats.org/package/2006/relationships',
    # Dublin Core document properties
    'dcmitype': 'http://purl.org/dc/dcmitype/',
    'dcterms': 'http://purl.org/dc/terms/'}

def getWords(fileObj):
  tree = etree.parse(fileObj)
  root = tree.getroot()
  table = root.find('.//w:tbl', nsprefixes)

  rows = table.findall('.//w:tr/', nsprefixes)
  rowsText = [re.sub('  +', ' ', ' '.join(_.itertext())) for _ in rows]
  rowsText = [_ for _ in rowsText if _ != '']

  # The indexes remove the header of the table, which is not needed any way :)
  return zip(rowsText[3::2], rowsText[4::2])

def parseDocx(filepath):
  with zipfile.ZipFile(filepath) as docxFile:
    return getWords(docxFile.open('word/document.xml'))
