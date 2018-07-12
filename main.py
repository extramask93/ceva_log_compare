import sys
import re
from abc import ABCMeta, abstractmethod

def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)

class IToken:
    __metaclass__ = ABCMeta
    @abstractmethod
    def GetNormalized(self):
        raise NotImplementedError()
    def __eq__(self, other):
        if self.GetNormalized()=="buggyman" or other.GetNormalized()=="buggyman":
            return True
        if isinstance(other, IToken):
            return self.GetNormalized() == other.GetNormalized()
        else:
           raise Exception("No defined comparison operator for this class")
class BuggyToken(IToken):
    tokenRegEx = "buggyman"
    def __init__(self, tokenString):
        self.tokenString = tokenString
    def GetNormalized(self):
        return self.tokenString.lower()
class MiscToken(IToken):
    tokenRegEx = ".*"
    def __init__(self, tokenString):
        self.tokenString = tokenString
    def GetNormalized(self):
        return self.tokenString.lower()
class InstructionNameToken(IToken):
    tokenRegEx = "^(sc0|ls0|ls1)\.[a-z0-9].+$"
    def __init__(self, tokenString):
        self.tokenString = tokenString
    def GetNormalized(self):
        self.tokenString.lower()
class NumberToken(IToken):
    tokenRegEx = "^[+-]?#[+-]?[0-9A-Fa-fx-x]*$"
    def __init__(self, tokenString):
        self.tokenString = tokenString
    def isHex(self,str):
        return 'x' in str.lower()
    def isNegative(self,str):
        return '-' in str.lower()
    def stripSign(self,str):
        return str.replace('-','')

    def stripHash(self,str):
        return str.replace('#','')
    def GetNormalized(self):
        correspondingNumber = 0
        signed = self.isNegative(self.tokenString)
        tempToken = self.stripHash(self.tokenString)
        tempToken = self.stripSign(tempToken)
        tempToken = tempToken.lower()
        if(self.isHex(tempToken)):
            correspondingNumber = int(tempToken,16)
        else:
            correspondingNumber = int(tempToken,10)
        if(signed):
            correspondingNumber = -correspondingNumber
        return "#"+str(correspondingNumber)
class OffsetToken(IToken):
    tokenRegEx = "^\(.*\+.*\)\..*$"
    def __init__(self, tokenString):
        self.tokenString = tokenString
    def Removepartheses(self,str):
        return str.replace('(','').replace(')','')
    def GetNormalized(self):
        str = self.Removepartheses(self.tokenString)
        tokenz = str.split('+')
        tokenz2 = []
        result = '('
        for token in tokenz:
            tokenz2.append(TokenFactory(token))
        for token in tokenz2:
            result = result + token.GetNormalized()+'+'
        result = rreplace(result,'.',').',1)
        result = rreplace(result, '+', '', 1)
        return result
class AddrToken(IToken):
    tokenRegEx = "^\(.*\)\..*$"
    def __init__(self, tokenString):
        self.tokenString = tokenString
    def GetNormalized(self):
        str = self.tokenString
        str = str.replace("(","").replace(")","")
        temp = str.split('.')
        str = temp[0]
        number = NumberToken(str).GetNormalized()
        return "("+number+")"+temp[1]
class RegAddrToken(IToken):
    tokenRegEx = "^\([^#].*\)\..*$"
    def __init__(self, tokenString):
        self.tokenString = tokenString
    def GetNormalized(self):
        str = self.tokenString
        str = str.replace("(","").replace(")","")
        temp = str.split('.')
        str = temp[0]
        str = str.lower()
        return "("+str+")"+temp[1]
class TokenFactory:
    @staticmethod
    def GetToken(tokenstr):
        if(re.search(BuggyToken.tokenRegEx,tokenstr) is not None):
            return BuggyToken(tokenstr)
        if(re.search(NumberToken.tokenRegEx,tokenstr) is not None):
            return NumberToken(tokenstr)
        if(re.search(InstructionNameToken.tokenRegEx,tokenstr) is not None):
            return InstructionNameToken(tokenstr)
        if(re.search(OffsetToken.tokenRegEx,tokenstr) is not None):
            return OffsetToken(tokenstr)
        if(re.search(RegAddrToken.tokenRegEx,tokenstr) is not None):
            return RegAddrToken(tokenstr)
        if(re.search(AddrToken.tokenRegEx,tokenstr) is not None):
            return AddrToken(tokenstr)
        else:
            return MiscToken(tokenstr)


def GetInstructions(lines):
    newlines = []
    for line in lines:
        match = re.search("(SC0|LS0|LS1|PC0|PC1|PCU|VPU|VPU1|VPU0).*$",line)
        if(match is None):
            continue
        else:
            newlines.append(match.group(0).lower())
    return newlines
def Compare(cmmlines,lstlines):
    maxFailedLinesToDisplay = 7
    cmmlines.pop(0)
    failCounter = 0
    linecnt = 7
    for cmm,lst in zip(cmmlines,lstlines):
        cmm=cmm.replace(",  ,",",BUGGYMAN,")
        lst = lst.replace(",  ,", ",BUGGYMAN,")
        lst = lst.replace(',',' ').replace('_',' ').replace('+',' ').replace("  "," ")
        cmm = cmm.replace(',',' ').replace('_',' ').replace('+',' ').replace("  "," ")
        tokensLST = lst.split()
        tokensCMM = cmm.split()
        lst2 = []
        for tokenLST,tokenCMM in zip(tokensLST,tokensCMM):
            a= TokenFactory.GetToken(tokenLST)
            b = TokenFactory.GetToken(tokenCMM)
            if(a == b):
                continue
            else:
                lst2.append((a.tokenString, b.tokenString))
        if (lst2 and failCounter < maxFailedLinesToDisplay):
            print("Difference in line {0}".format(linecnt))
            print("{0}(lst) - {1}(cmm) ==> [{2}<->{3}]".format(lst.lower().replace(',', ' '), cmm.lower().replace(',', ' '),lst2[0][0],lst2[0][1]))
            failCounter = failCounter + 1
        linecnt = linecnt+1

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
    cmmlines = GetInstructions(cmmlines)
    Compare(cmmlines,lstlines)

