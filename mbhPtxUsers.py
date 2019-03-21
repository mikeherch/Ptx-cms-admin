'''
Created on Mar 13, 2019

@author: Mike
'''
import mbhPtxRoot
import codecs
import sys

if __name__=="__main__":
    SettingsDirectory = "C:\\My Paratext 8 Projects\\"
    Project = "zzAkgUni"
    OutputFile = SettingsDirectory + "cms\\checktext.htm"
    Encoding = "65001"
    OptionIncludeUsers = "Mike Herchenroeder, DLA - PBTPNG, Martha Wade"
    OptionExcludeUsers = ""
    OptionIncludeProjects = "" # "AKG-Uni, AplUni, WARANUNI, ApalVB"
    OptionExcludeProjects = "ApalVB"
    OptionListSeparator = ","
    PSys = None
  

def main():
    writeout(htmlHeader)
    writeout(htmlStyle)
    writeout("<h2>Project Users</h2>\n")
    writeout("<table>\n")
    
    global PSys
    PSys = mbhPtxRoot.PtxDirectory(SettingsDirectory)
    strSep = OptionListSeparator if OptionListSeparator else ','
    
    listIncludeProjects = OptionIncludeProjects.split(strSep) if OptionIncludeProjects else []
    for i, item in enumerate(listIncludeProjects):
        listIncludeProjects[i] = listIncludeProjects[i].strip().lower()
        
    listExcludeProjects = OptionExcludeProjects.split(strSep) if OptionExcludeProjects else []
    for i, item in enumerate(listExcludeProjects):
        listExcludeProjects[i] = listExcludeProjects[i].strip().lower()
    
    listIncludeUsers = OptionIncludeUsers.split(strSep) if OptionIncludeUsers else []
    for i, item in enumerate(listIncludeUsers):
        listIncludeUsers[i] = item.strip().lower()
        
    listExcludeUsers = OptionExcludeUsers.split(strSep) if OptionExcludeUsers else []
    for i, item in enumerate(listExcludeUsers):
        listExcludeUsers[i] = item.strip().lower()

    # first pass; get filtered set of projects

    setAllProjectNames = set()
    for project in PSys.projects():
        blnInclude = False
        strName = project.name.lower()
        if listIncludeProjects:
            if strName in listIncludeProjects:
                blnInclude = True
        else:
            blnInclude = True
        if strName in listExcludeProjects:
            blnInclude = False
        if blnInclude:
            setAllProjectNames.add(project.name)
    
    
    # second  pass, collect allUsers
    setAllUsers = set()
    for project in PSys.projects():
        if project.name in setAllProjectNames:
            for user in project.users():
                strName = user.name.lower()
                blnInclude = False
                if listIncludeUsers:
                    if strName in listIncludeUsers:
                        blnInclude = True
                else:
                    blnInclude = True
                if strName in listExcludeUsers:
                    blnInclude = False
                if user.role == "None":
                    blnInclude = False
                if blnInclude:
                    setAllUsers.add(user.name)
            
    listAllUsers = list(setAllUsers)
    listAllUsers.sort()
#     print len(listAllUsers), listAllUsers
#     print setAllProjectNames
    
    # create dict of column positions keyed by user name and top row of array
    array = []
    listBlankRow = [''] * (len(listAllUsers) + 1)
    
    listRow = listBlankRow * 1
    dictUserColumns = {}
    for i, strUser in enumerate(listAllUsers):
        dictUserColumns[strUser] = i + 1
        listRow[i + 1] = strUser    # put user name in top row
    array.append(listRow)
    
    # pass three, load array
    for project in PSys.projects():
        if project.name in setAllProjectNames:
            listRow = listBlankRow * 1
            listRow[0] = project.name
            for user in project.users():
                if user.name in setAllUsers:
                    iCol = dictUserColumns[user.name]
                    listRow[iCol] = rolename(user.role)
            array.append(listRow)
    
    # Flip array here
    blnFlip = (len(setAllProjectNames) < len(setAllUsers))
#     blnFlip = False
    if blnFlip:
        array2 = []
        listBlankRow = [''] * (len(setAllProjectNames) + 1) 
        array2.append(listBlankRow * 1)
        
        for ignore in setAllUsers:
            array2.append(listBlankRow * 1)
        
        for iRow, listRow in enumerate(array):
            for iCol, strCell in enumerate(listRow):
                array2[iCol][iRow] = strCell
                
        array = array2

    # output first row
    array[0][0] = "&nbsp;"
    htmlLine = "<thead><tr>"
    for strCell in array[0]:
        htmlLine += ("<th>" + strCell + "</th>")
    htmlLine += "</tr></thead\n<tbody>"
    writeout(htmlLine)
    
    # output remaining rows
    for i, listRow in enumerate(array):
        if i == 0: continue     # skip first row (column headers)
        htmlLine = "<tr>"
        for strCell in listRow:
            if strCell:
                htmlLine += ("<td>" + strCell + "</td>")
            else:
                htmlLine += "<td>&nbsp;</td>"
        htmlLine += "</tr\n"
        writeout(htmlLine)

    writeout("</tbody></table>\n")
    writeout(htmlClose)

def rolename(strRole):
    aDict = {
        'Administrator': 'Administrator',
        'Consultant': 'Consultant',
        'None': '',
        'Observer': 'Observer',
        'Translator': 'Translator',
        'TeamMember': 'Translator'
    }
    if strRole in aDict:
        return aDict[strRole]
    else:
        return strRole
    
htmlHeader = """
<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<title>Paratext Projects</title>
"""
htmlStyle = """
<style>

body {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 1em;
    }

h2 {
    font-size: 1.3em;
    color: black;
    margin: 0.8em 0.4em;
    }

    
    
</style>
</head>
<body>
"""

htmlClose = """
</body>
</html>
"""

def cms():
    global TESTMODE
    TESTMODE = False
    sys.stdout = codecs.open(OutputFile,'w', 'utf-8')
    try:
        main()
    except:
        sys.stdout.flush()
        sys.stdout.close()
        raise

def test():
    global TESTMODE, FileProxyStdout
    TESTMODE = True
    FileProxyStdout = codecs.open(OutputFile,'w', 'utf-8')
    main()
    FileProxyStdout.close()

def writeout(strText):
    global TESTMODE, FileProxyStdout
    strWinText = strText.replace('\n', '\r\n')
    if TESTMODE:
        FileProxyStdout.write(strWinText)
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
