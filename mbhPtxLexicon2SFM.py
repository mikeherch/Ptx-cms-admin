'''
Created on Apr 3, 2019

@author: Mike
'''
import mbhPtxRoot
import codecs
import sys
import os.path

if __name__=="__main__":
    SettingsDirectory = "C:\\My Paratext 8 Projects\\"
    Project = "zzAkgUni"
    OutputFile = SettingsDirectory + "cms\\checktext.txt"
    Encoding = "65001"
    optionMorphemeFilter = 'Word'
    
g_LexFileName = 'Lexicon.xml'  
g_setMorphs = set()

def main():
    writeout("\\id %s/%s filtered by %s.\n" % (Project, g_LexFileName, optionMorphemeFilter))
    strPath = os.path.join(SettingsDirectory, Project, g_LexFileName)
#         print "Settings file:", strPath, '<br>'
    P = mbhPtxRoot.XMLParser(strPath)
    P.parseSkipUntil('Entries', P.BEGIN)
        
    strTag = ''
    while True:
        strToken, enumType = P.tokens.next()
        if enumType == P.EOF:
            break;
        elif enumType == P.BEGIN:
            strTag = strToken
            if strTag == 'Lexeme':
                strMorphType = strLang = strGloss = ''
                strToken, enumType = P.tokens.next() # should be attrs
                if enumType == P.ATTRS:
                    dictAttrs = P.parseAttrs(strToken)
                    strMorphType = dictAttrs['Type']
                    g_setMorphs.add(strMorphType)
                    strForm = dictAttrs['Form']
                    if passesFilter(strMorphType):
                        writeout("\\lx %s\n" % strForm)
                        writeout("\\ps %s\n" % strMorphType)
                    else:
                        P.parseSkipUntil('item', P.END)
                else:
                    say("Expected attributes at\n%s" % P.strLine)
                    P.parseSkipUntil('item', P.END)
            elif strTag == 'Entry':
                intSenseNum = 0
            elif strTag == 'Sense':
                intSenseNum += 1
                writeout("\\sn %d\n" % intSenseNum)
            elif strTag == 'Gloss':
                strToken, enumType = P.tokens.next() # should be attrs
                if enumType == P.ATTRS:
                    dictAttrs = P.parseAttrs(strToken)
                    strLang = dictAttrs['Language']
                    strToken, enumType = P.tokens.next() # should be CDATA
                    if enumType == P.CDATA:
                        strGloss = strToken
                        if strLang in ['en', 'eng']:
                            sfm = r'\ge'
                        else:
                            sfm = r'\gr'
                        writeout("%s %s\n" % (sfm, strGloss))
                else:
                    say("Expected language attribute at\n%s" % P.strLine)
                
        elif enumType == P.END:
            if strToken == 'Entry':
                writeout('\n')
            if strToken == 'Entries':
                break
        elif enumType == P.ATTRS:
            pass
        elif enumType == P.CDATA:
            pass
#     print 'Morph types', g_setMorphs
    
def passesFilter(morphType):
    if optionMorphemeFilter:
        return morphType.lower() in optionMorphemeFilter.lower()
    else:
        return True

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