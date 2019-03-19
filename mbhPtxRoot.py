'''
Created on Feb 20, 2019

@author: Mike Herchenroeder

'''
import sys
import os
import codecs
import xml.etree.ElementTree as ET


g_settingsDirectory = ''


class PtxDirectory:
    def __init__(self, settingsDir=''):
        global g_settingsDirectory
        if settingsDir:
            g_settingsDirectory = settingsDir
#         print 'g_settingsDirectory', g_settingsDirectory, '<br>'
        self.listProjectNames = []
        self.dictProjects = {}

        self.__getProjects()
            
    def __getProjects(self):
        """An iterator that returns a sequence of project names. A project is
        identified as a folder in settingsDirectory() that contains a file named 
        settings.xml
        """
#         print 'settingsDirctory', settingsDirectory(), '<br>'
        listFiles = os.listdir(settingsDirectory())
        for strFile in listFiles:
#             print strFile,'<br>'
            strPath = settingsDirectory() + strFile
            if os.path.isdir(strPath):
                # Found a folder. Does it contain a settings file?
#                 print strPath
                strSettingsPath = os.path.join(strPath,"Settings.xml")
                if os.path.exists(strSettingsPath):
                    strName = strFile
#                     print 'strName', strName, '<br>'
                    self.listProjectNames.append(strName)
                    aProject = Project(strName, strPath)
                    self.dictProjects[strName] = aProject
                    
    def project(self, name):
        if name in self.dictProjects:
            return self.dictProjects[name]
        else:
            return None
            
    def projects(self):
        for strName in self.listProjectNames:
            yield self.dictProjects[strName]
            
class Project:
    strUsersFileName = 'ProjectUserAccess.xml'
    strParametersFileName = 'settings.xml'
    
    def __init__(self, strName, strPath):
#         print "creating a project:", strName, strPath, '<br>'
        self.name = strName
        self.listUsers = []         # from ProjectUserAccess.xml
        self.langName = ''
        self.folderPath = strPath
        self.dictParameters = {}     # from settings.xml
        
        self.__parseParameters()
        self.languageName = self.getParameterValue('Language')
        strRawCode = self.getParameterValue('LanguageIsoCode')
        self.languageCode = strRawCode.rstrip(':')
        
        strTransInfo = self.getParameterValue('TranslationInfo')
        if strTransInfo:
            aList = strTransInfo.split(':')
            self.type = aList[0]
            self.basedOn = aList[1] if len(aList) > 1 else ''
        else:
            self.type = "Standard ?"
            self.basedOn = ''
    def users(self):
        if len(self.listUsers) == 0:
            self.__parseUsers()
        for aUser in self.listUsers:
            yield aUser

    def __parseUsers(self):
        strPath = os.path.join(self.folderPath, self.strUsersFileName)
        if os.path.exists(strPath):
#             tree = ET.parse(strPath)
#             root = tree.getroot()
            P = XMLParser(strPath)
            while True:
                blnSuccess = P.parseSkipUntil('User', P.BEGIN)
                if not blnSuccess:
                    break
                aUser = User(P)
                if aUser.role:
                    self.listUsers.append(aUser)
                
    def administrators(self):
        for user in self.users():
            if user.role == 'Administrator':
                yield user
                
    def translators(self):
        for user in self.users():
            if user.role == 'Translator':
                yield user
                
    def consultants(self):
        for user in self.users():
            if user.role == 'Consultant':
                yield user   

    def observers(self):
        for user in self.users():
            if user.role == 'Observer':
                yield user
    
    def getParameterValue(self, name):
        if name in self.dictParameters:
            return self.dictParameters[name]
        else:
            return ''
        
    def __parseParameters(self):
#         tree = ET.parse(os.path.join(self.folderPath, self.strParametersFileName))
#         root = tree.getroot()
        strPath = os.path.join(self.folderPath, self.strParametersFileName)
#         print "Settings file:", strPath, '<br>'
        P = XMLParser(strPath)
        strToken, enumType = P.tokens.next()
        if strToken != "ScriptureText":
            say("First element is %s. Expected: %s" % (strToken, "Scripture Text"))
            
        strTag = ''
        while True:
            strToken, enumType = P.tokens.next()
            if enumType == P.EOF:
                break;
            elif enumType == P.BEGIN:
                strTag = strToken
            elif enumType == P.ATTRS:
                pass
            elif enumType == P.CDATA:
                self.dictParameters[strTag] = strToken
            elif enumType == P.END:
                if strToken == strTag:
                    if strTag not in self.dictParameters:
                        self.dictParameters[strTag] = ''
                elif strToken == "ScriptureText":
                    break
                else:
                    say("unexpected end tag: %s \nin %s\n" % (strToken, P.strLine))
                strTag = ''
                
            else:
                say("unexpected token: %s \nin %s\n" % (strToken, P.strLine))
    
class User:
    def __init__(self, parser):
        """ elemUser is an XML Element
        """
        self.name = ''
        self.role = ''
        self.__parseUser(parser)
        
    def __parseUser(self, parser):
        """Use parser to import properties of the User. Assume the parser has 
        already consumed and yielded the begin tag <User>, but not the tag 
        attributes. Continue parsing until the end tag </User> has been consumed.
        """
        P = parser
        strToken, enumType = P.tokens.next()
        if enumType == P.ATTRS:
            dictAttrs = P.parseAttrs(strToken)
            self.name = dictAttrs.get('UserName', '')
            strToken, enumType = P.tokens.next()
        while True:
            if (strToken, enumType) == ('User', P.END):
                return
            elif (strToken, enumType) == ('Role', P.BEGIN):
                self.role = P.parseGetCData()
            elif enumType == P.EOF:
                return
            strToken, enumType = P.tokens.next()
                    
class XMLParser:
    # XML token types
    EOF = 0
    BEGIN = 1
    END = 2
    CDATA = 3
    ATTRS = 4
    UNDEF = 5
    PROC = 6
    
    def __init__(self, strFilePath, blnIgnoreProc=True):
        """Initalize XMLParser. 
            strFilePath - path of XML file to parse
            blnIgnoreProc - If True, processor directives <?...?> will be ignored
        """
        self.name = os.path.split(strFilePath)
        self.path = strFilePath
        self.fileXML = codecs.open(strFilePath,'r', 'utf_8_sig')
        self.tokens = self.xmlTokens()  #instance of interator
        self.blnIgnoreProc = blnIgnoreProc
       
        self.strLine = self.fileXML.readline()
        self.ungottenchar = ''
        self.indexChar = 0
        
#     def __getattr__(self, name):
#         if name == "name": return self.name
#         if name == "path": return self.path
#         if name == "language": return self.language
#         if name == "stages": return self.listStages
#         raise NameError, name

    def __repr__(self):
        return '%s, stages:%i, @%s' % (self.name, len(self.listStages),self.path)
    
    def xmlTokens(self):
        """A generator that reads self.fileXML and yields a sequence of  
        2-tuples consisting of an XML token and the type of token. 
        Yield '' on EOF. Subsequent function calls after EOF will continue to yield ''.
        """
        while(True):
            enumTokenType = self.UNDEF
            c = self.getchar()
            # skip all whites space
            while c <= " ":  # some kind of whitespace or control character
                if c == '': 
                    yield '', self.EOF
                    break
                else:
                    c = self.getchar()
            if c == '': yield '', self.EOF
            elif c == '<':
                c = self.getchar()
                if c == '': yield '', self.EOF
                elif c == '/':
                    enumTokenType = self.END
                    strTagName = self.getUpToAny('>')
                    c = self.getchar()  # consume the '>'
                    yield strTagName, enumTokenType
                elif c == '?':
                    enumTokenType = self.PROC   # processor directive
                    strData = ''
                    while True:
                        c = self.getchar()
                        if c == '?' and self.peekchar() == '>':
                            break
                        strData += c
                    c = self.getchar() # consume '>' after '?'
                    if not self.blnIgnoreProc:
                        yield strData, enumTokenType 
                else:
                    enumTokenType = self.BEGIN
                    strTagName = c  #first letter of tag name
                    while True:
                        c = self.getchar()
                        if c == ' ':
                            yield strTagName, enumTokenType # begin tag
                            if not self.peekchar() in '/>':
                                enumTokenType = self.ATTRS
                                # The following fails if an attribute value includes either '/' or '>'
                                strAttrs = self.getUpToAny('/>')
                                strAttrs = strAttrs.strip()
                                if strAttrs:
                                    yield strAttrs, enumTokenType

                            c = self.getchar()
                            if c == '>': #close begin tag
                                break
                            elif c == '/':
                                c = self.getchar()
                                if c == '>':    #Empty tag, return implied end tag
                                    yield strTagName, self.END
                                break
                            else: break # might be EOF
                                
                        elif c == '>':
                            yield strTagName, enumTokenType
                            break
                        elif c == '/': # looks like an empty tag
                            yield strTagName, enumTokenType
                            c = self.getchar()  # should be '>'
                            if c == '>':
                                yield strTagName, self.END # yield implied end tag
                        elif c == '': 
                            yield '', self.EOF
                            break
                        else:
                            strTagName += c
                    
            else:
                enumTokenType = self.CDATA
                strData = ''
                while True:
                    if c == '<':
                        yield strData, enumTokenType
                        self.ungetchar(c)
                        break
                    elif c == '&':
                        strData += self.getEntity()
                    elif c == '':
                        yield strData, enumTokenType
                        break
                    else:
                        strData += c
                    c = self.getchar()
    
        while True:
            yield '', self.EOF   # Keep yielding EOF 
            
    def getchar(self):
        """Get the next character from self.fileXML. If a character was
        saved by ungetchar() return the ungottenchar instead.
        Do not CR or LF.
        """
        if self.ungottenchar:
            c = self.ungottenchar
            self.ungottenchar = ''
            return c
        elif self.strLine:
            if self.indexChar >= len(self.strLine): # reached EOL
                self.strLine = self.fileXML.readline()
                self.indexChar = 0
                return self.getchar()
            else:
                c = self.strLine[self.indexChar]
                if c in '\r\n':
                    self.indexChar = len(self.strLine) # EOL, skip cr lf
                    return self.getchar()   # return char on next line
                else:
                    self.indexChar += 1
                    return c
        else: # EOF
            return ''
        
    def ungetchar(self, c):
        self.ungottenchar = c
        
    def peekchar(self):
        c = self.getchar()
        self.ungetchar(c)
        return c
    
    def getUpToAny(self,strEnd):
        """Reads characters from file until any character in strEnd is read.
        The read string is returned. The end character is put back using 
        ungetchar()
        """
        s = ''
        c = self.getchar()
        while c not in strEnd:
            s += c
            c = self.getchar()
        self.ungetchar(c)
        return s
    
    def getEntity(self):
        """Input and parse XML Character entity, returning interpreted character.
        Assume '&' has already been read.
        """
        strEntity = self.getUpToAny(';')
        dictEntities = {
            'apos': "'", 'amp':'&', 'gt':'>', 'lt':'<', 'quot':'"'}
        if strEntity in dictEntities:
            self.getchar()  #consume ';'
            return dictEntities[strEntity]
        else:
            return '&' + strEntity + ';'
    
#     def getPCDATA(self, cdata):
#         strData = ''
#         i = 0
#         while i < len(cdata):
#             c = cdata[i]
#             i += 1
#             if c == '<':
#                 break
#             elif c == '&':
#                 # decode entity
#                 j = cdata.find(';', i)
#                 if j > -1: 
#                     strCode = cdata[i:j]
#                     dictEntities = {
#                         'apos': "'", 'amp':'&', 'gt':'>', 'lt':'<', 'quot':'"'}
#                     if strCode in dictEntities:
#                         strData += dictEntities[strCode]
#                     else: # unknown entity
#                         strEntity = '&' + strCode + ';'
#                         print "Unknown entity: %s\r\n" % strEntity
#                         strData += strEntity
#                     i = j+1                        
#                 else:
#                     strData += c   # bogus ampersand or bad entity. Just pass it.
#             else:
#                 strData += c
#         return strData
#         unicode.find
#     def parseEncodedText(self, strTagName, strLanguage='en'):
#         """ Each encoded text consists of a sequence of <item> elements.
#         Each <item> element contains a pair of <string>elements. The first 
#         string contains a language code, and the second the text. Return the 
#         text for the selected language (strLanguage), or the text for English
#         if no text for the selected language is found.
#         """
#         strEnglishText = ''
#         strPreferredText = ''
#         while True:
#             strToken, enumType = self.tokens.next()
#             if (strToken, enumType) == (strTagName, self.END):
#                 if strPreferredText:
#                     return strPreferredText
#                 else:
#                     return strEnglishText
#             elif (strToken, enumType) == ('item', self.END):
#                 pass
#             elif (strToken, enumType) == ('item', self.BEGIN):
#                 # Found <item> tag, read 2 <string> elements
#                 strText = ''
#                 strLang = ''
#                 strToken, enumType = self.tokens.next()
#                 if (strToken, enumType) == ('string', self.BEGIN):
#                     # get language from first string element'
#                     strToken, enumType = self.tokens.next()
#                     if (strToken, enumType) == ('string', self.END):
#                         strLang = ''
#                     elif enumType == self.CDATA:
#                         strLang = strToken
#                         strToken, enumType = self.tokens.next()
#                         if (strToken, enumType) != ('string', self.END):
#                             break
#                     else:
#                         break
#                     # get text from second string
#                     strToken, enumType = self.tokens.next()
#                     if (strToken, enumType) == ('string', self.BEGIN):
#                         strToken, enumType = self.tokens.next()
#                         if (strToken, enumType) == ('string', self.END):
#                             strText = ''
#                         elif enumType == self.CDATA:
#                             strText = strToken
#                             strToken, enumType = self.tokens.next()
#                             if (strToken, enumType) != ('string', self.END):
#                                 break
#                         else:
#                             break
#                     if strLang:
#                         self.AllLanguages.add(strLang)
#                     if strLang == strLanguage:
#                         strPreferredText = strText
#                     elif strLang == 'en':
#                         strEnglishText = strText
#                     else:
#                         pass # keep looping
#             else:
#                 break
#         return 'Unparsable input: ' + strToken
    
#     def parseAll(self):
#         self.parseStages()
#         self.parseSkipUntil('BasePlanName', self.BEGIN)
#         self.basePlanName = self.parseGetCData()
#             

    def parseSkipUntil(self, strTagName, enumTagType):
        while True:
            strToken, enumType = self.tokens.next()
            if (strToken, enumType) == (strTagName, enumTagType):
                return True
            elif enumType == self.EOF:
                return False
            
       
    def parseGetCData(self):
        """ Reads one CDATA token and one end tag token and returns the CDATA."""
        strToken, enumType = self.tokens.next()
        if enumType == self.ATTRS:
            strToken, enumType = self.tokens.next() #ignore ATTRs
        if enumType == self.END:
            return ''
        elif enumType == self.CDATA:
            strCdata = strToken
            strToken, enumType = self.tokens.next() # presumably an end tag
            return strCdata

    def parseAttrs(self, attrs, aDict=None):
        """Parse the string attrs and place each attribute/value pair into a 
        dictionary. Return the dictionary.
        """
        dictAttrs = aDict if aDict else dict()
        if not attrs:
            return dictAttrs
        iEquals = attrs.find('=', 0)
        if iEquals == -1:
            say("Unable to parse attrs; %s" % attrs)
            return dictAttrs
        strName = attrs[0:iEquals].rstrip()
        iQuot1 = attrs.find('"', iEquals + 1) #skip over any spaces
        iQuot2 = attrs.find('"', iQuot1 + 1)
        strValue = attrs[iQuot1+1:iQuot2]
        dictAttrs[strName] = strValue
        strRestOfAttrs = attrs[iQuot2+1:].strip()
        if strRestOfAttrs:
            return self.parseAttrs(strRestOfAttrs, dictAttrs)
        else:
            return dictAttrs
        
        
            
        
# def getXmlRootElement(path):
# #     path2 = r"C:\My Paratext 8 Projects\abc\settings.xml"
#     tree = ET.parse(path)
#     root = tree.getroot()
# #     strEncoding = 'utf_8_sig'
# #     aFile = codecs.open(path2, 'r', strEncoding)
# #     strText = aFile.read()
# #     aFile.close()
# #     aParser = ET.XMLParser(encoding='UTF-8')
# #     root = ET.fromstring(strText.encode('utf-8'))
#     return root

def settingsDirectory():
    """ Find the directory with Paratext 8 projects using the Windows registry """
    global g_settingsDirectory
    
    if g_settingsDirectory:
        return g_settingsDirectory
    else:
        from _winreg import OpenKey, EnumValue, HKEY_LOCAL_MACHINE
    
        strPath = r"SOFTWARE\WOW6432Node\Paratext\8"
        try:
            aKey = OpenKey(HKEY_LOCAL_MACHINE, strPath)
            for i in [0,1,2,3,4,5,6,7]:
                aName, aValue, irrelevant = EnumValue(aKey,i)
                if aName == 'Settings_Directory':
                    g_settingsDirectory = aValue
                    return aValue
            return None
    
        except WindowsError:
            # The registry key was not found
            return None
        except:
            raise   
        
def say(strText):
    """ Write strText to stderr
    """
    strNL = '' if strText[-1] == '\n' else '\n'
    sys.stderr.write(strText + strNL)
    
def test():
    Psys = PtxDirectory()
    print "Testing\n"
    print "Paratext root: %s\n " % settingsDirectory()
    print "First 5 projects:"
    i=0
    for aProject in Psys.projects():
        print aProject.name, aProject.languageName, aProject.languageCode
        s = " " + aProject.type
        if aProject.basedOn:
            s += (' based on:' + aProject.basedOn )
        print s
        for i, user in enumerate(aProject.users()):
            if i > 3: break
            print "User %s" % user.name
        for user in aProject.administrators():
            print '', user.name, user.role
        for user in aProject.translators():
            print '', user.name, user.role
        for user in aProject.consultants():
            print '', user.name, user.role
        for user in aProject.observers():
            print '', user.name, user.role
        i += 1
        if i > 5:
            break
        
    aProj = Psys.project('ABU-Uni')
    print aProj.name
    
if __name__=="__main__":
    test()