'''
Created on Feb 21, 2019

@author: Michael Herchenroeder
'''
# import mbh_junkbits
import mbhPtxRoot
import codecs
import sys

if __name__=="__main__":
    SettingsDirectory = "C:\\My Paratext 8 Projects\\"
    Project = "zzAkgUni"
#     OptionBasePlan = '' # name of base plan to search from, form GUI options
#     OptionLanguage = 'en'
#     OptionStagesExpanded = 'y'
#     OptionTasksExpanded = 'n'
#     OptionChecks = 'none'
    OutputFile = SettingsDirectory + "cms\\checktext.htm"
    Encoding = "65001"
    OptionProjectsExpanded = 'N'
    PSys = None
  

def main():
    global PSys
    PSys = mbhPtxRoot.PtxDirectory(SettingsDirectory)

    writeout(htmlHeader)
    writeout(htmlStyle)
    writeout("<h2>Paratext Projects</h2>\n")
    htmlLine = ''

    for project in PSys.projects():
        htmlProjHeader = buildHtmlProjHeader(project)
        strFullName = project.getParameterValue('FullName')
        listProjDetails = list()
#         
        listUsers = []
        for user in project.administrators():
            listUsers.append(user.name)
        htmlAdmins = "<u>Administrators:</u> " + ', '.join(listUsers)
        listProjDetails.append(htmlAdmins)
 
        listUsers = []
        for user in project.translators():
            listUsers.append(user.name)
        htmlTrans = "<u>Translators:</u> " + ', '.join(listUsers)
        listProjDetails.append(htmlTrans)
 
        listUsers = []
        for user in project.consultants():
            listUsers.append(user.name)
        htmlCons = "<u>Consultants:</u> " + ', '.join(listUsers)
        listProjDetails.append(htmlCons)
 
 
        listUsers = []
        for user in project.observers():
            listUsers.append(user.name)
        htmlObservers = "<u>Observers:</u> " + ', '.join(listUsers)
        listProjDetails.append(htmlObservers)
 
        htmlProject = buildHtmlProject(
            htmlProjHeader, strFullName, listProjDetails)
        writeout(htmlProject)
        
    writeout("</div>\n")
    writeout(htmlClose)
       
def buildHtmlProjHeader(proj):
    html = buildHtmlNameAndLang(proj) + ', '
    html += proj.type
    if proj.basedOn:
        baseProject = PSys.project(proj.basedOn)
        if baseProject:
            html += (' based on ' + buildHtmlNameAndLang(baseProject))
        else:
            html += (' based on <b>' + proj.basedOn + '</b>')
    return html
    
def buildHtmlNameAndLang(proj):
    html = "<b>%s</b> - %s (%s)\n" % (proj.name, proj.languageName, proj.languageCode)
    return html

def buildHtmlProject(htmlName, strFullName, listUsers):
    htmlItems = "<ul>\n"
    if strFullName:
        strDetail = asPCDATA(strFullName)
        htmlItems += "<li>%s</li>\n" % strDetail
      
    for htmlRole in listUsers:
        htmlItems += "<li>%s</li>\n" % htmlRole
    
    htmlItems += "</ul>\n"
    return buildDetails(
        htmlName, htmlItems, 'stage', asBool(OptionProjectsExpanded))
    
def buildDetails(strSummary, htmlDetails, summaryClass='nada', blnOpen=False):
    if blnOpen: strOpen = ' Open'
    else: strOpen = ''
        
    htmlSummary = '<summary class="%s">\n%s\n</summary>\n' % (summaryClass, strSummary)
    y = '<details%s>\n%s%s</details>\n' % (strOpen, htmlSummary, htmlDetails)
    return y
   
def asPCDATA(aStr):
    return(aStr)

def asBool(aStr):
    return aStr.upper() in ['Y', 'YES' 'T', 'TRUE']

htmlHeader = """
<!DOCTYPE html>
<html lang="en-US">
<head>
<title>Paratext Projects</title>
"""
htmlStyle = """
<style>

body {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 1em;
    color: #000000;
    }

h2 {
    font-size: 1.3em;
    color: black;
    margin: 0.8em 0.4em;
    }
    
ul {
    list-style-type: none;
    margin: 0px;
    }

.nada    { color: black; }

.header {
    background-color: #FFD966;
    color: black;
    font-weight:bold;
    }

.stage, summary {
    border-radius: 0.4em;
    margin-bottom: 0.1em;
    padding: 0.1em 0 0.1em 0.6em;
    }

.stage {
    font-size: 1.1em;
    color: black;
    background-color: #e4f885;
    margin-bottom: 0.3em;
    }
    
summary.task {
    background-color: #f0f0f0;
    }
summary.check {
    background-color: #f0fee5;
    }
    
.details {
    margin-left: 3.0em;
    }
    
div.langs {
    margin-top: 1em;
    }

.a { min-width: 20em; }
.b { min-width: 50em; color: green;}
.c { min-width: 500px; }
.d { width: 20em; }
.e { width: 20em; }
.symbol { font-family: "Lucida Console", monospace; }

.explain {
    padding: 0px;
    margin: 0px 0px 0px 2.6em;
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
