'''
Created on Jun 13, 2019

@author: Mike
'''
import sys
import re 
import codecs
import os.path
import StringIO

if __name__=="__main__":
    SettingsDirectory = "C:\\My Paratext 8 Projects\\"
    Project = "zzAkgUni"
    optxfScopeElement = 'item'
#     optxfXmlFileName = 'Lexicon.xml'
#     optxfXmlFileName = r"..\_StandardPlans\SIL Compact Plan - Rev 1.xml"
    optxfXmlFileName = r"Interlinear_en\Interlinear_en_MAT.xml"
    optxfScopeOnly = 'Y'
    optxfAcceptFilter = r""
    optxfRejectFilter = r""
    optxfSearchRegex = r"C:\Dox\Temp\regexTest.txt"
    optxfReplaceRegex = r""
    OutputFile = SettingsDirectory + "cms\\checktext.txt"
    Encoding = "65001"
    
def main(xml):
    blnScopeOnly = optxfScopeOnly.upper() in ['Y', 'YES', 'T', 'TRUE']
    listScopes = getScopes(xml)
    
    try:
        patAccept = re.compile(optxfAcceptFilter) if optxfAcceptFilter else None
    except:
        say("Invalid Accept Filter Regex: %s\n" % optxfAcceptFilter)
        return
    
    try:
        patReject = re.compile(optxfRejectFilter) if optxfRejectFilter else None
    except:
        say("Invalid Reject Filter Regex: %s\n" % optxfRejectFilter)
        return
    
    if optxfSearchRegex:
        if os.path.exists(optxfSearchRegex):
            listSearchReplace =  parseRegexFile(optxfSearchRegex)
        else:
            try:
                patSearch = re.compile(optxfSearchRegex)
            except:
                say("Invalid Search Regex: %s\n" % optxfSearchRegex)
                return
            listSearchReplace = [patSearch, optxfReplaceRegex]
    else:
        listSearchReplace = None
    
    for S in listScopes:
        blnAccept = applyRegex(S.text, patAccept) if patAccept else True
        blnReject = applyRegex(S.text, patReject) if patReject else False
        
        if blnScopeOnly:
            S.textBefore = ""
            
        if blnAccept and not blnReject:
            if listSearchReplace:
                strNew = S.text
                for patSearch, strReplace in listSearchReplace:
                    strNew = re.sub(patSearch, strReplace, strNew)
                    S.text = strNew
            writeout(S.textBefore + S.indent + S.text + S.eol)
        else:
            writeout(S.textBefore)
        
class XmlText:
    def __init__(self, filename):
        self.index = 0
        
        if os.path.exists(filename):
            strFile = filename
        elif filename[0:3] == "..\\":
            strFile = os.path.join(SettingsDirectory, filename[3:])
        else:
            strFile = os.path.join(SettingsDirectory, Project, filename)
            
        strFile = os.path.realpath(strFile)
            
        try:
            fileXML = codecs.open(strFile, 'r', 'utf_8')
            self.text = fileXML.read()
            fileXML.close()
        except IOError:
            say("Cannot open file: %s\n" % strFile)
            self.text = ''
            return

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

def parseRegexFile(path):
    """ Sample regex file to be parsed:
    # This is a comment
        "search pattern1"  >  "replace pattern1"    # comment
        '\s*(abc|xyz)'     >  'stuff \1'            # delimiters either " or '
    """
    try:
        aFile = codecs.open(path, 'r', 'utf-8-sig')
    except:
        raise
    
    listRegex = []
    strEntire = aFile.read()
    aStream = StringIO.StringIO(strEntire)
    for strLine in aStream:
        if not strLine: continue  
        if strLine[0] == "#": continue
        m = re.match(r"\s*([\"\'])(.+?)\1\s+>\s+([\"\'])(.+?)\3\s*(#.*)?", strLine)
        if m:
            strSearch = m.group(2)
            aPattern = re.compile(strSearch)
            strReplace = m.group(4)
            listRegex.append((aPattern, strReplace))
        else:
            say("Invalid syntax in %s: \n   %s\n" % (path,strLine))
    return listRegex

def cms():
    global TESTMODE
    TESTMODE = False
    xml = XmlText(optxfXmlFileName)
    if xml.text:
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
    if xml.text:
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
