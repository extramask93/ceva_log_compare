import sys
import re
def GetInstructions(lines):
    newlines = []
    for line in lines:
        match = re.search("(SC0.*)$",line)
        if(match is None):
            continue
        else:
            newlines.append(match.group(0))
    return newlines
def Compare(cmmlines,lstlines):
    maxFailedLinesToDisplay = 7
    failCounter = 0
    linecnt = 7
    for cmm,lst in zip(cmmlines,lstlines):
        lst = lst.replace(' ','').replace('_','')
        cmm = cmm.replace(' ','').replace('_','')
        if(cmm != lst and failCounter<maxFailedLinesToDisplay):
            print("Difference in line {0}".format(linecnt))
            print("{0}(lst) - {1}(cmm)".format(lst.lower().replace(',',' '), cmm.lower().replace(',',' ')))
            failCounter = failCounter+1
        linecnt = linecnt+1
def ToHex(list):
    ishex = 0
    newlist = []
    for line in list:
        ishex = 0
        res = re.search('#\(?([0-9A-Fa-fx-x]*)([,\)])',line)
        if(res is not None):
            number = res.group(1)
            if('x' in number):
                ishex = 1
            if(not ishex):
                integer = int(number,10)
                hexed = hex(integer)
                old = res.group(0)
                new = '#'+hexed+res.group(2)
                line = line.replace(old,new)
            else:
                integer = int(number,16)
                hexed = hex(integer)
                old = res.group(0)
                new = '#'+hexed+res.group(2)
                line = line.replace(old,new)
        newlist.append(line)
    return newlist
def ToUpper(list):
    newlist = []
    for elem in list:
        elem = elem.upper()
        newlist.append(elem)
    return newlist
if __name__ == '__main__':
    argc = len(sys.argv)
    argv = sys.argv
    cmm = open(argv[1],'r')
    lst = open("testsFromTrace.lst",'r')
    cmmlines = cmm.readlines()
    lstlines = lst.readlines()
    cmm.close()
    lst.close()
    lstlines = GetInstructions(lstlines)
    if(argc <= 2):
        lstlines = ToHex(lstlines)
    lstlines = ToUpper(lstlines)
    cmmlines = GetInstructions(cmmlines)
    cmmlines.pop(0)
    if(argc <= 2):
        cmmlines = ToHex(cmmlines)
    cmmlines = ToUpper(cmmlines)
    Compare(cmmlines,lstlines)

