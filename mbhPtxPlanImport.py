'''
@author: Mike Herchenroeder
'''
import os.path
import codecs
from mbhPtxRoot import XMLParser

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
        
    def parseTask(self, aPlan, parser):
        """Parse input up thru </Task> and store results in self.
        """
        while True:
            strToken, enumType = parser.tokens.next()
            if enumType == parser.EOF:
                break;
            elif enumType == parser.ATTRS:
                pass    #ignore attrs
            elif (strToken, enumType) == ('Names',parser.BEGIN):
                s = aPlan.parseEncodedText(parser, 'Names', aPlan.language)
                self.name = s
            elif (strToken, enumType) == ('Type',parser.BEGIN):
                s = parser.parseGetCData()
                self.type = s
            elif (strToken, enumType) == ('EasiestBooksVPD',parser.BEGIN):
                s = parser.parseGetCData()
                self.easiestBooksVPD = s
            elif (strToken, enumType) == ('EasyBooksVPD',parser.BEGIN):
                s = parser.parseGetCData()
                self.easyBooksVPD = s
            elif (strToken, enumType) == ('ModerateBooksVPD',parser.BEGIN):
                s = parser.parseGetCData()
                self.moderateBooksVPD = s
            elif (strToken, enumType) == ('DifficultBooksVPD',parser.BEGIN):
                s = parser.parseGetCData()
                self.difficultBooksVPD = s
            elif (strToken, enumType) == ('Availability',parser.BEGIN):
                s = parser.parseGetCData()
                self.availability = s
            elif (strToken, enumType) == ('EditingRequired',parser.BEGIN):
                self.availability = 'Yes'
                parser.parseSkipUntil('EditingRequired', parser.END)
            elif (strToken, enumType) == ('Descriptions',parser.BEGIN):
                s = aPlan.parseEncodedText(parser, 'Descriptions', aPlan.language)
                self.description = s
            elif (strToken, enumType) == ('Task',parser.END):
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
        
    def parseCheck(self, parser):
        while True:
            strToken, enumType = parser.tokens.next()
            if enumType == parser.EOF:
                break;
            elif enumType == parser.ATTRS:
                pass    # ignore attrs
            elif (strToken, enumType) == ('BasicCheckType', parser.BEGIN):
                self.basicCheckType = parser.parseGetCData()
            elif (strToken, enumType) == ('Type', parser.BEGIN):
                self.type = parser.parseGetCData()
            elif (strToken, enumType) == ('AutoGrantEditRights', parser.BEGIN):
                self.autoGrantEditRights = parser.parseGetCData()
            elif (strToken, enumType) == ('Details', parser.BEGIN):
                self.details = parser.parseGetCData()
            elif (strToken, enumType) == ('Check', parser.END):
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

    def parseStage(self, aPlan, parser):
        """Parses from line after <Stage> thru </Stage> and stores values of a
        names, descriptions, list of tasks, list of checks.
        """
        while True:
            strToken, enumType = parser.tokens.next()
            if enumType == parser.EOF:   #EOF, shouldn't happen
                break;
            elif enumType == parser.ATTRS:
                pass    # ignore attrs
            elif (strToken, enumType) == ('Task', parser.BEGIN):
                aTask = Task()
                aTask.parseTask(aPlan, parser) # up thru </Task>
                self.tasks.append(aTask)
            elif (strToken, enumType) == ('Check', parser.BEGIN):
                aCheck = aPlan.parseCheck(parser)
                self.checks.append(aCheck)
            elif (strToken, enumType) == ('Names', parser.BEGIN):
                self.name = aPlan.parseEncodedText(parser, 'Names', aPlan.language) # up thru </Names>
            elif (strToken, enumType) == ('Descriptions', parser.BEGIN):
                self.description = aPlan.parseEncodedText(parser, 'Descriptions', aPlan.language) # up thru </Descriptions>
            elif (strToken, enumType) == ('Stage', parser.END):
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

    def __init__(self, strName, strFilePath, strLang = 'en'):
        self.name = strName
        self.basePlanName = ''
        self.path = strFilePath
        self.filePlan = codecs.open(strFilePath,'r', 'utf-8')
#         self.tokens = self.xmlTokens()
        self.listStages = []
        self.language = strLang
        self.AllLanguages = set()
        
        self.strLine = self.filePlan.readline()
        self.ungottenchar = ''
        self.indexChar = 0
        
    def __repr__(self):
        return '%s, stages:%i, @%s' % (self.name, len(self.listStages),self.path)
    
    def close(self):
        if not self.filePlan.closed:
            self.filePlan.close()
    
    def stages(self):
        return self.listStages
            
    def parseEncodedText(self, parser, strTagName, strLanguage='en'):
        """ Each encoded text consists of a sequence of <item> elements.
        Each <item> element contains a pair of <string>elements. The first 
        string contains a language code, and the second the text. Return the 
        text for the selected language (strLanguage), or the text for English
        if no text for the selected language is found.
        """
        strEnglishText = ''
        strPreferredText = ''
        while True:
            strToken, enumType = parser.tokens.next()
            if (strToken, enumType) == (strTagName, parser.END):
                if strPreferredText:
                    return strPreferredText
                else:
                    return strEnglishText
            elif (strToken, enumType) == ('item', parser.END):
                pass
            elif (strToken, enumType) == ('item', parser.BEGIN):
                # Found <item> tag, read 2 <string> elements
                strText = ''
                strLang = ''
                strToken, enumType = parser.tokens.next()
                if (strToken, enumType) == ('string', parser.BEGIN):
                    # get language from first string element'
                    strToken, enumType = parser.tokens.next()
                    if (strToken, enumType) == ('string', parser.END):
                        strLang = ''
                    elif enumType == parser.CDATA:
                        strLang = strToken
                        strToken, enumType = parser.tokens.next()
                        if (strToken, enumType) != ('string', parser.END):
                            break
                    else:
                        break
                    # get text from second string
                    strToken, enumType = parser.tokens.next()
                    if (strToken, enumType) == ('string', parser.BEGIN):
                        strToken, enumType = parser.tokens.next()
                        if (strToken, enumType) == ('string', parser.END):
                            strText = ''
                        elif enumType == parser.CDATA:
                            strText = strToken
                            strToken, enumType = parser.tokens.next()
                            if (strToken, enumType) != ('string', parser.END):
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
        parser = XMLParser(self.path)
        self.parseStages(parser)
        parser.parseSkipUntil('BasePlanName', parser.BEGIN)
        self.basePlanName = parser.parseGetCData()
        
    def parseStages(self, parser):
        """Parses <Stages> to </Stages> and stores a list of stages in
        self.listStages. Returns nothing.
        """
        parser.parseSkipUntil('Stages', parser.BEGIN)
        iCount = 0
        while True:
            strToken, enumType = parser.tokens.next()
            if enumType == parser.EOF:
                break;
            if (strToken, enumType) == ('Stage', parser.BEGIN):
                aStage = Stage()
                iCount += 1
                aStage.number = iCount
                aStage.parseStage(self, parser)
                aStage.summarizeChecks()
                self.listStages.append(aStage) # up thru </Stage>
            elif (strToken, enumType) == ('Stages', parser.END):
                break   #All Done
              
    def parseCheck(self, parser):
        """Returns a Check. 
        """
        aCheck = Check()
        aCheck.parseCheck(parser)
        return aCheck

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
    
