'''
Created on Feb 20, 2019

@author: Mike Herchenroeder

'''
import os
import codecs
import xml.etree.ElementTree as ET


g_settingsDirectory = ''


class PtxDirectory:
    def __init__(self, settingsDir=''):
        global g_settingsDirectory
        if settingsDir:
            g_settingsDirectory = settingsDir
        print 'g_settingsDirectory', g_settingsDirectory, '<br>'
        self.listProjectNames = []
        self.dictProjects = {}

        self.__getProjects()
            
    def __getProjects(self):
        """An iterator that returns a sequence of project names. A project is
        identified as a folder in settingsDirectory() that contains a file named 
        settings.xml
        """
        print 'settingsDirctory', settingsDirectory(), '<br>'
        listFiles = os.listdir(settingsDirectory())
        for strFile in listFiles:
            print strFile,'<br>'
            strPath = settingsDirectory() + strFile
            if os.path.isdir(strPath):
                # Found a folder. Does it contain a settings file?
                print strPath
                strSettingsPath = os.path.join(strPath,"Settings.xml")
                if os.path.exists(strSettingsPath):
                    strName = strFile
                    print 'strName', strName, '<br>'
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
        print "creating a project:", strName, strPath, '<br>'
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
            root = getXmlRootElement(strPath)
            for elemUser in root:
                aUser = User(elemUser)
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
        print "Settings file:", strPath, '<br>'
        root = getXmlRootElement(strPath)
        for elemParam in root:
            self.dictParameters[elemParam.tag] = elemParam.text
    
class User:
    def __init__(self, elemUser):
        """ elemUser is an XML Element
        """
        self.name = elemUser.attrib['UserName']
        elemRole = elemUser.find('Role')
        strRole = elemRole.text
        if strRole == 'None':
            self.role = ''
        elif strRole == 'TeamMember':
            self.role = 'Translator'
        else:
            self.role = elemRole.text
                    
def getXmlRootElement(path):
#     path2 = r"C:\My Paratext 8 Projects\abc\settings.xml"
    tree = ET.parse(path)
    root = tree.getroot()
#     strEncoding = 'utf_8_sig'
#     aFile = codecs.open(path2, 'r', strEncoding)
#     strText = aFile.read()
#     aFile.close()
#     aParser = ET.XMLParser(encoding='UTF-8')
#     root = ET.fromstring(strText.encode('utf-8'))
    return root

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