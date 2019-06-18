'''
Created on Jun 13, 2019

@author: Mike
'''
import sys
import re 
import codecs
import os.path

if __name__=="__main__":
    SettingsDirectory = "C:\\My Paratext 8 Projects\\"
    Project = "zzAkgUni"
    optxfScopeElement = 'item'
#     optxfXmlFileName = 'Lexicon.xml'
    optxfXmlFileName = "C:\My Paratext 8 Projects\_StandardPlans\SIL Compact Plan - Rev 1.xml"
    optxfAcceptFilter = r">en<"
    optxfRejectFilter = r""
    optxfSearchRegex = r"\btext\b"
    optxfReplaceRegex = r"story"
    OutputFile = SettingsDirectory + "cms\\checktext.txt"
    Encoding = "65001"
    
def main(xml):
    listScopes = getScopes(xml)
    
    patAccept = re.compile(optxfAcceptFilter) if optxfAcceptFilter else None
    patReject = re.compile(optxfRejectFilter) if optxfRejectFilter else None
    patSearch = re.compile(optxfSearchRegex) if optxfSearchRegex else None
    
    for S in listScopes:
        blnAccept = applyRegex(S.text, patAccept) if patAccept else True
        blnReject = applyRegex(S.text, patReject) if patReject else False
         
        if blnAccept and not blnReject:
            if patSearch:
                strNew = re.sub(patSearch, optxfReplaceRegex, S.text)
                S.text = strNew
            writeout(S.textBefore + S.indent + S.text + S.eol)
        else:
            writeout(S.textBefore)
        
class XmlText:
    def __init__(self, filename):
        self.index = 0
        
        if os.path.exists(filename):
            strFile = filename
        else:
            strFile = os.path.join(SettingsDirectory, Project, filename)
            
        fileXML = codecs.open(strFile, 'r', 'utf_8')
        self.text = fileXML.read()
        fileXML.close()

        self.hasBOM = True if self.text[0] == u'\uFEFF' else False
        
    def startIndex(self):
        if self.hasBOM:
            return 1
        else:
            return 0
        
    def encoding(self):
        if self.hasBOM:
            return 'utf_8_sig'
        else:
            return 'utf_8'
            
        
class Scope:
    def __init__(self):
        self.text = ''
        self.textBefore = ''
        self.indent = ''
        self.eol = ''
    

def applyRegex(text, pattern):
    m = pattern.search(text)
    return True if m else False
    
def getScopes(xml):
    """Reads through the text of an XML file and locates all the scope elements.
    It returns a list of tuples each containing, three strings. The first string
    is the text of a scope element, and the second string is the text between 
    the last scope element and the current scope element, less the indent 
    preceding the scope element, and the third is the indent that precedes the 
    scope element. The last tuple consists of an empty string, and the text from
    the last scope to the end of the file.
    """
    strTagName = optxfScopeElement.strip('<>')
    strEndTag = '</' + strTagName + '>'
    strPattern = r"\<" + strTagName + r"(?=[ />])"
    patScopeElement = re.compile(strPattern)
    
    aList = []
    iStart = xml.startIndex()
    
    # find beginning of all scope elements
    for m in patScopeElement.finditer(xml.text):
        S = Scope()
        iTagStart, iNameEnd = m.span()
        # find end of scope element
        iEndOfTag = xml.text.find('>', iNameEnd)
        if xml.text[iEndOfTag - 1] == '/':
            iEndOfElement = iEndOfTag + 1   # this is an empty element
        else:
            iEndOfElement = xml.text.find(strEndTag, iEndOfTag) + len(strEndTag)
            
        # Look for EOL immediately following iEndOfElement
        iEOL = iEndOfElement
        iLen = len(xml.text)
        while iEOL < iLen and xml.text[iEOL] in '\r\n':
            iEOL += 1

        # calculate length of indent
        indexStart = iTagStart
        while indexStart >= 0:
            if xml.text[indexStart - 1] in "\t ":
                indexStart -= 1
            else:
                break

        S.text = xml.text[iTagStart:iEndOfElement]
        S.textBefore = xml.text[iStart:indexStart]
        S.indent = xml.text[indexStart:iTagStart]
        S.eol = xml.text[iEndOfElement:iEOL]
        aList.append(S)
        iStart = iEOL
    lastS = Scope()
    lastS.textBefore = xml.text[iStart:]
    aList.append(lastS)
    return aList

def cms():
    global TESTMODE
    TESTMODE = False
    xml = XmlText(optxfXmlFileName)
    sys.stdout = codecs.open(OutputFile,'w', xml.encoding())
    try:
        main(xml)
    except:
        sys.stdout.flush()
        sys.stdout.close()
        raise

def test():
    global TESTMODE, FileProxyStdout
    TESTMODE = True
    xml = XmlText(optxfXmlFileName)
    FileProxyStdout = codecs.open(OutputFile,'w', xml.encoding())
    main(xml)
    FileProxyStdout.close()
    

def writeout(strText):
    global TESTMODE, FileProxyStdout
#     strWinText = strText.replace('\n', '\r\n')
    if TESTMODE:
        FileProxyStdout.write(strText)
    else:
        sys.stdout.write(strText)

def say(strText):
    """ Write strText to stderr
    """
    strNL = '' if strText[-1] == '\n' else '\n'
    sys.stderr.write(strText + strNL)

if __name__=="__main__":
    test()
else:
    cms()