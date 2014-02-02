import xml.etree.ElementTree as etree
import zipfile
import re

ODF_NAMESPACES = {
  'anim': "urn:oasis:names:tc:opendocument:xmlns:animation:1.0",
  'chart': "urn:oasis:names:tc:opendocument:xmlns:chart:1.0",
  'config': "urn:oasis:names:tc:opendocument:xmlns:config:1.0",
  'dc': "http://purl.org/dc/elements/1.1/",
  'dom': "http://www.w3.org/2001/xml-events",
  'dr3d': "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0",
  'draw': "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
  'fo': "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
  'form': "urn:oasis:names:tc:opendocument:xmlns:form:1.0",
  'math': "http://www.w3.org/1998/Math/MathML",
  'meta': "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
  'number': "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0",
  'of': "urn:oasis:names:tc:opendocument:xmlns:of:1.2",
  'office': "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
  'ooo': "http://openoffice.org/2004/office",
  'oooc': "http://openoffice.org/2004/calc",
  'ooow': "http://openoffice.org/2004/writer",
  'presentation': "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0",
  'rdfa': "http://docs.oasis-open.org/opendocument/meta/rdfa#",
  'rpt': "http://openoffice.org/2005/report",
  'script': "urn:oasis:names:tc:opendocument:xmlns:script:1.0",
  'smil': "urn:oasis:names:tc:opendocument:xmlns:smil-compatible:1.0",
  'style': "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
  'svg': "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
  'table': "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
  'text': "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
  'xforms': "http://www.w3.org/2002/xforms",
  'xlink': "http://www.w3.org/1999/xlink",
  'xsd': "http://www.w3.org/2001/XMLSchema",
  'xsi': "http://www.w3.org/2001/XMLSchema-instance",
  'manifest': "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0",
  'xml': 'http://www.w3.org/XML/1998/namespace'
  } 

def getWords(fileObj):
  tree = etree.parse(fileObj)
  root = tree.getroot()
  table = root.find('.//table:table', ODF_NAMESPACES)

  rows = table.findall('.//table:table-row/', ODF_NAMESPACES)
  rowsText = [re.sub('  +', ' ', ' '.join(_.itertext())) for _ in rows]

  return zip(rowsText[::2], rowsText[1::2])

def parseOdt(filepath):
  with zipfile.ZipFile(filepath) as odtFile:
    return getWords(odtFile.open('content.xml'))
