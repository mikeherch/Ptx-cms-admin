'''
Created on Oct 20, 2017

@author: MikeH
'''
import os.path
import codecs

class Task:
    def __init__(self):
        self.name = ''
        self.description = ''
        self.type = ''
        self.availability = 'No'
        self.editingRequired = ''
        self.easiestBooksVPD = 1000
        self.easyBooksVPD = 1000
        self.moderateBooksVPD = 1000
        self.difficultBooksVPD = 1000
        
    def parseTask(self, aPlan):
        """Parse input up thru </Task> and store results in self.
        """
        while True:
            strToken, enumType = aPlan.tokens.next()
            if enumType == aPlan.EOF:
                break;
            elif enumType == aPlan.ATTRS:
                pass    #ignore attrs
            elif (strToken, enumType) == ('Names',aPlan.BEGIN):
                s = aPlan.parseEncodedText('Names', aPlan.language)
                self.name = s
            elif (strToken, enumType) == ('Type',aPlan.BEGIN):
                s = aPlan.parseGetCData()
                self.type = s
            elif (strToken, enumType) == ('EasiestBooksVPD',aPlan.BEGIN):
                s = aPlan.parseGetCData()
                self.easiestBooksVPD = s
            elif (strToken, enumType) == ('EasyBooksVPD',aPlan.BEGIN):
                s = aPlan.parseGetCData()
                self.easyBooksVPD = s
            elif (strToken, enumType) == ('ModerateBooksVPD',aPlan.BEGIN):
                s = aPlan.parseGetCData()
                self.moderateBooksVPD = s
            elif (strToken, enumType) == ('DifficultBooksVPD',aPlan.BEGIN):
                s = aPlan.parseGetCData()
                self.difficultBooksVPD = s
            elif (strToken, enumType) == ('Availability',aPlan.BEGIN):
                s = aPlan.parseGetCData()
                self.availability = s
            elif (strToken, enumType) == ('EditingRequired',aPlan.BEGIN):
                self.availability = 'Yes'
                aPlan.parseSkipUntil('EditingRequired', aPlan.END)
            elif (strToken, enumType) == ('Descriptions',aPlan.BEGIN):
                s = aPlan.parseEncodedText('Descriptions', aPlan.language)
                self.description = s
            elif (strToken, enumType) == ('Task',aPlan.END):
                break
        
class Check:
    def __init__(self):
        self.type = ''
        self.basicCheckType = ''
        self.autoGrantEditRights = False
        self.details = ''
        self.postponedBooks = ''
        
    def __getattr__(self, name):
        if name == "name":
            if self.basicCheckType > '':
                return self.basicCheckType
            if self.type == 'SpellCheckUnknown': return 'Words with Unknown spelling status'
            if self.type == 'SpellCheckIncorrect': return 'Words with Incorrect spelling status'
            if self.type == 'PassageCheck': return 'Parallel Passages'
            if self.type == 'InterlinearGlosses': return 'Interlinear glosses approved'
            if self.type == 'BiblicalTermRenderings': return 'Biblical Terms renderings found'
            if self.type == 'SpellingNoteCheck': return 'Spelling Discussion Notes'
            if self.type == 'RenderingNoteCheck': return 'Renderings Discussion Notes'
            if self.type == 'NotesAssignedToMeCheck': return 'Notes Assigned to Me'
            
            listDetails = self.details.split('|')
            if self.type == 'BackTranslationChapterVerse':
                strBackTransProject = listDetails[0] # details before pipe
                return 'Back translation (%s) verse check' % strBackTransProject
            if self.type == 'BackTranslationStatus': 
                strBackTransProject = listDetails[0] # details before pipe
                return 'Back translation (%s) status complete' % strBackTransProject
            if self.type == 'NoteCheck':
                strNoteType = self.noteType(listDetails[0]) # To do or Conflict
                return 'Project Notes (%s)' % strNoteType 
            if self.type == 'DerivedProjectNoteCheck':
                strDerivedProject = listDetails[0]
                strNoteType = self.noteType(listDetails[1])
                return 'Derived Project Notes (%s - %s)' % (strDerivedProject, strNoteType)
            return 'No Name'
        if name == "availability": return 'Auto'            
        raise NameError, name
        
    def parseCheck(self, aPlan):
        while True:
            strToken, enumType = aPlan.tokens.next()
            if enumType == aPlan.EOF:
                break;
            elif enumType == aPlan.ATTRS:
                pass    # ignore attrs
            elif (strToken, enumType) == ('BasicCheckType', aPlan.BEGIN):
                self.basicCheckType = aPlan.parseGetCData()
            elif (strToken, enumType) == ('Type', aPlan.BEGIN):
                self.type = aPlan.parseGetCData()
            elif (strToken, enumType) == ('AutoGrantEditRights', aPlan.BEGIN):
                self.autoGrantEditRights = aPlan.parseGetCData()
            elif (strToken, enumType) == ('Details', aPlan.BEGIN):
                self.details = aPlan.parseGetCData()
            elif (strToken, enumType) == ('Check', aPlan.END):
                break
        return
    
    def noteType(self, strValue):
        if strValue == '1': return 'To Do'
        if strValue == '-1': return 'Conflict'
        return ''
        
class Stage:
    def __init__(self):
        self.name = ''
        self.number = 0
        self.description = ''
        self.tasks = []
        self.checks = []
        self.basicChecks = []       # list of check names
        self.spellingChecks = []    # list of check names
        self.notesChecks = []       # list of check names
        self.passageChecks = []     # list of check names
        self.interlinearChecks = []     # list of check names
        self.biblicalTermsChecks = []   # list of check names
        self.backTranslationChecks = [] # list of check names

    def parseStage(self, aPlan):
        """Parses from line after <Stage> thru </Stage> and stores values of a
        names, descriptions, list of tasks, list of checks.
        """
        while True:
            strToken, enumType = aPlan.tokens.next()
            if enumType == aPlan.EOF:   #EOF, shouldn't happen
                break;
            elif enumType == aPlan.ATTRS:
                pass    # ignore attrs
            elif (strToken, enumType) == ('Task', aPlan.BEGIN):
                aTask = Task()
                aTask.parseTask(aPlan) # up thru </Task>
                self.tasks.append(aTask)
            elif (strToken, enumType) == ('Check', aPlan.BEGIN):
                aCheck = aPlan.parseCheck()
                self.checks.append(aCheck)
            elif (strToken, enumType) == ('Names', aPlan.BEGIN):
                self.name = aPlan.parseEncodedText('Names', aPlan.language) # up thru </Names>
            elif (strToken, enumType) == ('Descriptions', aPlan.BEGIN):
                self.description = aPlan.parseEncodedText('Descriptions', aPlan.language) # up thru </Descriptions>
            elif (strToken, enumType) == ('Stage', aPlan.END):
                break
    
    def summarizeChecks(self):
        """Combine checks into seven categories. For each category, store the
        names of the checks in the category.
        """
        for aCheck in self.checks:
            if 'Basic' in aCheck.type:
                self.basicChecks.append(aCheck.name)
            if 'Spell' in aCheck.type:
                self.spellingChecks.append(aCheck.name)
            if 'Note' in aCheck.type:
                self.notesChecks.append(aCheck.name)
            if 'BackTran' in aCheck.type:
                self.backTranslationChecks.append(aCheck.name)
            if 'Passage' in aCheck.type:
                self.passageChecks.append(aCheck.name)
            if 'Biblical' in aCheck.type:
                self.biblicalTermsChecks.append(aCheck.name)
            
class ProjectPlan:
    # XML token types
    EOF = 0
    BEGIN = 1
    END = 2
    CDATA = 3
    ATTRS = 4
    UNDEF = 5
    
    def __init__(self, strName, strFilePath, strLang = 'en'):
        self.name = strName
        self.basePlanName = ''
        self.path = strFilePath
        self.filePlan = codecs.open(strFilePath,'r', 'utf-8')
        self.tokens = self.xmlTokens()
        self.listStages = []
        self.language = strLang
        self.AllLanguages = set()
        
        self.strLine = self.filePlan.readline()
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
    
    def close(self):
        if not self.filePlan.closed:
            self.filePlan.close()
    
    def xmlTokens(self):
        """A generator that reads self.filePlan and yields a sequence of  
        2-tuples consisting of an XML token and they type of token. 
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
                else:
                    enumTokenType = self.BEGIN
                    strTagName = c  #first letter of tag name
                    while True:
                        c = self.getchar()
                        if c == ' ':
                            yield strTagName, enumTokenType # begin tag
                            if not self.peekchar() in '/>':
                                enumTokenType = self.ATTRS
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
        """Get the next character from self.filePlan. If a character was
        saved by ungetchar() return the ungottenchar instead.
        Do not CR or LF.
        """
        if self.ungottenchar:
            c = self.ungottenchar
            self.ungottenchar = ''
            return c
        elif self.strLine:
            if self.indexChar >= len(self.strLine): # reached EOL
                self.strLine = self.filePlan.readline()
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
    def stages(self):
        return self.listStages
            
    def parseEncodedText(self, strTagName, strLanguage='en'):
        """ Each encoded text consists of a sequence of <item> elements.
        Each <item> element contains a pair of <string>elements. The first 
        string contains a language code, and the second the text. Return the 
        text for the selected language (strLanguage), or the text for English
        if no text for the selected language is found.
        """
        strEnglishText = ''
        strPreferredText = ''
        while True:
            strToken, enumType = self.tokens.next()
            if (strToken, enumType) == (strTagName, self.END):
                if strPreferredText:
                    return strPreferredText
                else:
                    return strEnglishText
            elif (strToken, enumType) == ('item', self.END):
                pass
            elif (strToken, enumType) == ('item', self.BEGIN):
                # Found <item> tag, read 2 <string> elements
                strText = ''
                strLang = ''
                strToken, enumType = self.tokens.next()
                if (strToken, enumType) == ('string', self.BEGIN):
                    # get language from first string element'
                    strToken, enumType = self.tokens.next()
                    if (strToken, enumType) == ('string', self.END):
                        strLang = ''
                    elif enumType == self.CDATA:
                        strLang = strToken
                        strToken, enumType = self.tokens.next()
                        if (strToken, enumType) != ('string', self.END):
                            break
                    else:
                        break
                    # get text from second string
                    strToken, enumType = self.tokens.next()
                    if (strToken, enumType) == ('string', self.BEGIN):
                        strToken, enumType = self.tokens.next()
                        if (strToken, enumType) == ('string', self.END):
                            strText = ''
                        elif enumType == self.CDATA:
                            strText = strToken
                            strToken, enumType = self.tokens.next()
                            if (strToken, enumType) != ('string', self.END):
                                break
                        else:
                            break
                    if strLang:
                        self.AllLanguages.add(strLang)
                    if strLang == strLanguage:
                        strPreferredText = strText
                    elif strLang == 'en':
                        strEnglishText = strText
                    else:
                        pass # keep looping
            else:
                break
        return 'Unparsable input: ' + strToken
    
    def parseAll(self):
        self.parseStages()
        self.parseSkipUntil('BasePlanName', self.BEGIN)
        self.basePlanName = self.parseGetCData()
        
    def parseStages(self):
        """Parses <Stages> to </Stages> and stores a list of stages in
        self.listStages. Returns nothing.
        """
        self.parseSkipUntil('Stages', self.BEGIN)
        iCount = 0
        while True:
            strToken, enumType = self.tokens.next()
            if enumType == self.EOF:
                break;
            if (strToken, enumType) == ('Stage', self.BEGIN):
                aStage = Stage()
                iCount += 1
                aStage.number = iCount
                aStage.parseStage(self)
                aStage.summarizeChecks()
                self.listStages.append(aStage) # up thru </Stage>
            elif (strToken, enumType) == ('Stages', self.END):
                break   #All Done
            

    def parseSkipUntil(self, strTagName, enumTagType):
        while True:
            strToken, enumType = self.tokens.next()
            if (strToken, enumType) == (strTagName, enumTagType):
                return
            elif enumType == self.EOF:
                return
            
   
    def parseCheck(self):
        """Returns a Check. 
        """
        aCheck = Check()
        aCheck.parseCheck(self)
        return aCheck
    
    
    
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

    def quickReport(self):
        pass
       
def basePlans():
    """An iterator that yields a sequence of tuples consisting of base plan 
    name and path. A base plan is an XML file in 
    My Paratext 8 Projects\_StandardPlans
    """
    strPlansDirectory = os.path.join(settingsDirectory(),"_StandardPlans")
    listFiles = os.listdir(strPlansDirectory)
    for strFile in listFiles:
        if strFile[-4:] == '.xml':
            strName = strFile[0:-4]
            strPath = os.path.join(strPlansDirectory, strFile)
            yield strName, strPath
            

def findBasePlan(strSearch):
    """ Searches for a base plan whose name contains strSearch, and returns
    the name of the plan and its path. If more than one plan matches
    strSearch, the first one found is returned.
    """
    for strName, strPath in basePlans():
        if strSearch in strName:
            return strName, strPath
    return '',''
        
def findProjectProgress(strProject):
    if not strProject:
        return '',''
    strPath = os.path.join(
        settingsDirectory(), strProject, 'ProjectProgress.xml')
    if os.path.exists(strPath):
        strName = strProject + ' ProjectProgress.xml'
        return strName, strPath
    else:
        return '',''
        
def ProjectNames():
    """An iterator that returns a sequence of project names. A project is
    identified as a folder in settingsDirectory() that contains a file named 
    settings.xml
    """
    listFiles = os.listdir(settingsDirectory())
    for strFile in listFiles:
        strPath = settingsDirectory() + strFile
        if os.path.isdir(strPath):
            # Found a folder. Does it contain a settings file?
            strSettingsPath = os.path.join(strPath,"Settings.xml")
            if os.path.exists(strSettingsPath):
                yield strFile

def settingsDirectory():
    # Find the directory with Paratext 8 projects using the windows registry
    from _winreg import OpenKey, EnumValue, HKEY_LOCAL_MACHINE

    strPath = r"SOFTWARE\WOW6432Node\Paratext\8"
    try:
        aKey = OpenKey(HKEY_LOCAL_MACHINE, strPath)
        for i in [0,1,2,3,4,5]:
            aName, aValue, irrelevant = EnumValue(aKey,i)
            if aName == 'Settings_Directory':
                return aValue + '\\'
        return None
    
    except WindowsError:
        # The registry key was not found
        return None
    except:
        raise            

def test():
    print "Testing\n"
    print "Paratext root: %s\n " % settingsDirectory()
    print "First 5 projects:"
    i=0
    for strProject in ProjectNames():
        i += 1
        if i < 5:
            print strProject
        
    for strName, strPath in basePlans():
        print strName, '    ', strPath

    strName, strPath = findBasePlan("PBT")
    print "Found base plan: ", strName
    assert strName != None
    assert strPath != None
    aBasePlan = ProjectPlan(strName, strPath)
    assert aBasePlan.name == strName
    
    aBasePlan.parseAll()
    print "Number of stages ", len(aBasePlan.listStages)
    assert aBasePlan.filePlan.closed == False
    aBasePlan.close()
    
if __name__=="__main__":
    test()
    
