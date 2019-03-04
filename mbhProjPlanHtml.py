'''
Created on April 11, 2018

@author: MikeH
'''
import mbhProjectPlanImport
import sys
import codecs
# from mbhCommon import say

if __name__=="__main__":
    SettingsDirectory = "C:\\My Paratext 8 Projects\\"
    Project = "zzPbtPln"
    OptionBasePlan = '' # name of base plan to search from, form GUI options
    OptionLanguage = 'en'
    OptionStagesExpanded = 'y'
    OptionTasksExpanded = 'n'
    OptionChecks = 'none'
    OutputFile = SettingsDirectory + "cms\\checktext.htm"
    Encoding = "65001"
  

def main():
    aBasePlan = None
    try:
        if len(OptionBasePlan.strip()) > 0:
            strName, strPath = mbhProjectPlanImport.findBasePlan(OptionBasePlan)
            if not strName:
                say("Could not find base plan: %s." % OptionBasePlan)
                return
        else:
            strName, strPath = mbhProjectPlanImport.findProjectProgress(Project)
            if not strName:
                say("Could not find ProjectProgress for: %s." % Project)
                return
            
        aBasePlan = mbhProjectPlanImport.ProjectPlan(strName, strPath, OptionLanguage)
        aBasePlan.parseAll()
        writereport(aBasePlan)
    except:
        raise
    finally:
        if aBasePlan: aBasePlan.close()


def writereport(aPlan):
    dictAllChecks = {
        'basic' : [],
        'spelling' : [],
        'notes' : [],
        'passage' : [],
        'interlinear' : [],
        'terms' : [],
        'backtranslation' : []
        }
    
    writeout(htmlHeader)
    writeout(htmlStyle)
    writeout("<h2>%s -- based on %s</h2>\n" % (aPlan.name, aPlan.basePlanName))
    htmlLine = ''
    htmlLine += buildLabel("Stages", 'a')
    htmlLine += buildLabel("   Task Names", 'b')
    htmlLine += buildLabel(" - When can task start?", 'c')
    htmlLine += buildLabel(", Mark as complete", 'd')
#     htmlLine += buildLabel("Require Edit", 'e')
#     writeout("<div class=header>\n%s</div>\n" % htmlLine)
    for aStage in aPlan.listStages:
        listStageDetails = list()
        
        for aTask in aStage.tasks:
            htmlTaskRow = ""
            htmlTaskRow += buildSymbol(aTask.availability)
            htmlTaskRow += buildSymbol(aTask.type)
            htmlTaskRow += buildLabel(aTask.name, 'nada')
            htmlTaskRow += (', ' + buildEffort(aTask))
            if aTask.description:
                strDescription = aTask.description
            else:
                strDescription = '(no description)'
            htmlDetails = '<div class="details">%s</div>' % strDescription
            htmlTask = buildDetails(
                htmlTaskRow, htmlDetails, 'task', asBool(OptionTasksExpanded))
            listStageDetails.append(htmlTask)
        if OptionChecks.lower() != 'none':
            collectChecks('basic', aStage.basicChecks, dictAllChecks)
            collectChecks('spelling', aStage.spellingChecks, dictAllChecks)
            collectChecks('notes', aStage.notesChecks, dictAllChecks)
            collectChecks('passage', aStage.passageChecks, dictAllChecks)
            collectChecks('interlinear', aStage.interlinearChecks, dictAllChecks)
            collectChecks('terms', aStage.biblicalTermsChecks, dictAllChecks)
            collectChecks('backtranslation', aStage.backTranslationChecks, dictAllChecks)
            
            if dictAllChecks['basic']:
                htmlCheck = buildCheck('Basic Checks', dictAllChecks['basic'])
                listStageDetails.append(htmlCheck)
            if dictAllChecks['spelling']:
                htmlCheck = buildCheck('Spelling Checks', dictAllChecks['spelling'])
                listStageDetails.append(htmlCheck)
            if dictAllChecks['notes']:
                htmlCheck = buildCheck('Notes Checks', dictAllChecks['notes'])
                listStageDetails.append(htmlCheck)
            if dictAllChecks['passage']:
                htmlCheck = buildCheck('Parallel Passages Checks', dictAllChecks['passage'])
                listStageDetails.append(htmlCheck)
            if dictAllChecks['interlinear']:
                htmlCheck = buildCheck('Interlinear Glosses Checks', dictAllChecks['interlinear'])
                listStageDetails.append(htmlCheck)
            if dictAllChecks['terms']:
                htmlCheck = buildCheck('Biblical Term Renderings Checks', dictAllChecks['terms'])
                listStageDetails.append(htmlCheck)
            if dictAllChecks['backtranslation']:
                htmlCheck = buildCheck('Back Translation Checks', dictAllChecks['backtranslation'])
                listStageDetails.append(htmlCheck)
     

    
        htmlStage = buildHtmlStage(
            aStage.name, aStage.number, aStage.description, listStageDetails)
        writeout(htmlStage)
        
    writeout('\n<div class="langs"><b>Symbols used on this page</b> ')
    writeout(buildSymbolUsed('WhenProjectStarts'))
    writeout(buildSymbolUsed('WhenStageIsComplete'))
    writeout(buildSymbolUsed('WhenBookStarts'))
    writeout(buildSymbolUsed('AfterPreviousTaskForChapter'))
    writeout(buildSymbolUsed('Auto'))
    writeout(buildSymbolUsed('ManualByChapter'))
    writeout(buildSymbolUsed('ManualByProject'))
    writeout(buildSymbolUsed('Manual'))
    
    writeout('\n<div class="langs"><b>Languages present in project plan:</b> ')
    for strLang in aPlan.AllLanguages:
        writeout("%s, " % strLang)
    writeout("</div>\n")
    writeout(htmlClose)
    
def collectChecks(strKey, listChecks, aDict):
    if OptionChecks.lower() == 'new':
        aDict[strKey] = listChecks
    elif OptionChecks.lower() == 'all':
        aDict[strKey] += listChecks
    else:
        pass
    
def buildCheck(strName, listDetails):
    htmlSummary = buildSymbol('Auto') + buildSymbol('') + strName
    strDetails = '; '.join(listDetails)
    htmlDetails = '<div class="details">%s</div>' % strDetails
    htmlCheck = buildDetails(
        htmlSummary, htmlDetails, 'check', asBool(OptionTasksExpanded))
    return htmlCheck
    
def friendlyTerm(strTerm):
    aDict = {'WhenProjectStarts':'When project starts',
             'WhenStageIsComplete':'When previous stage is complete',
             'WhenBookStarts':'When Book Starts',
             'AfterPreviousTaskForChapter':'After Previous Task',
             'AfterPreviousTaskForBook':'After Previous Task',
             'ManualByChapter':'Once per chapter',
             'ManualByProject':'Once per project',
             'Manual':'Once per book',
             'Auto' : 'Automatic Check'}
    if strTerm in aDict:
        return aDict[strTerm]
    else:
        return strTerm
    
def symbolFor(strTerm):
    aDict = {'WhenProjectStarts':'&#x2592;',
             'WhenStageIsComplete':'&#x039E;',
             'WhenBookStarts':'&#x25A1;',
             'AfterPreviousTaskForChapter':'&#x2191;',
             'AfterPreviousTaskForBook':'&#x2191;',
             'ManualByChapter':'C',
             'ManualByProject':'P',
             'Manual':'B',
             'Auto' : '&#x221E;'}

    if strTerm in aDict:
        return aDict[strTerm]
    else:
        return '&nbsp'

def buildHtmlStage(strName, intNumber, strDescription, listTasks):
    htmlItems = "<ul>\n"
    if strDescription:
        strDetail = asPCDATA(strDescription)
    else:
        strDetail = "(no description)"
        
    htmlItems += "<li>%s</li>\n" % strDetail
        
    for htmlTask in listTasks:
        htmlItems += "<li>%s</li>\n" % htmlTask
    
    htmlItems += "</ul>\n"
    htmlFullName = "Stage %i: %s" % (intNumber, asPCDATA(strName))
    return buildDetails(
        htmlFullName, htmlItems, 'stage', asBool(OptionStagesExpanded))
    
# def buildHtmlTask(htmlNameEtc, strDescription):
#     htmlSummary = "<p>%s</p>\n"
#     if strDescription:
#         htmlDetails = asPCDATA(strDescription)
#     else:
#         htmlDetails = "(no description)"
#     return buildDetails(htmlSummary, htmlDetails, False)
    
def buildDetails(strSummary, htmlDetails, summaryClass='nada', blnOpen=False):
    if blnOpen: strOpen = ' Open'
    else: strOpen = ''
        
    htmlSummary = '<summary class="%s">\n%s\n</summary>\n' % (summaryClass, strSummary)
    y = '<details%s>\n%s%s</details>\n' % (strOpen, htmlSummary, htmlDetails)
    return y

def buildTable(htmlHeader, listRows):
    if htmlHeader:
        htmlRows = htmlHeader + '\n'
    else:
        htmlRows = ''
    for htmlRow in listRows:
        htmlRows += (htmlRow + '\n')
    return "<table>\n%s</table>\n" % htmlRows

def buildRow(listCells, cellType='td'):
    htmlCells = ''
    for htmlCell in listCells:
        htmlCells += "<%s>%s</%s>" % (cellType, htmlCell, cellType)
    return "<tr>\n%s\n</tr>\n" % htmlCells

def buildLabel(aStr, strClass):
    return '<span class="%s">%s</span>' % (strClass, asPCDATA(aStr))

def buildSymbol(strTerm):
    strSymbol = symbolFor(strTerm)
    return '<span class="symbol">%s&nbsp;</span>' % strSymbol
        
def buildEffort(aTask):
    htmlEffort = '[' + aTask.easiestBooksVPD + ', ' + aTask.easyBooksVPD + ', ' \
    + aTask.moderateBooksVPD + ', ' + aTask.difficultBooksVPD + ']'
    return htmlEffort
    
def buildSymbolUsed(strTerm):
    strSymbol = symbolFor(strTerm)
    strFriendly = friendlyTerm(strTerm)
    htmlPara = '<p class=explain><span class="symbol">%s&nbsp;-&nbsp;</span>%s</p>' % (strSymbol, strFriendly)
    return htmlPara
    
def paddedPhrase(strPhrase, intWidth):
    intPadding = intWidth - len(strPhrase)
    if intPadding < 1:
        intPadding = 1
    return strPhrase + (' ' * int(intPadding * 1.3))
    
    
def asPCDATA(aStr):
    return(aStr)

def asBool(aStr):
    return aStr.upper() in ['Y', 'YES' 'T', 'TRUE']

htmlHeader = """
<!DOCTYPE html>
<html lang="en-US">
<head>
<title>Project Plan</title>
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
    font-weight:bold;
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