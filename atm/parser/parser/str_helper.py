# coding=utf-8

import re
import string
from log_helper import LogHelper
import pylev

class StrHelper:
    
    def __init__(self):
        LogHelper.log("created")
    
    @staticmethod
    def split(inputStr, segLen, sep):
        outputList = []
        
        inputStrList = inputStr.split(sep)
        output = ''
        while len(inputStrList) > 0:
            entry = inputStrList.pop(0)
            output = output + entry + sep;
            if len(output) >= segLen:
                outputList.append(output)
                output = ''
        
        if len(output) > 0:
            outputList.append(output)
            
        return outputList

    @staticmethod
    def getWordSimilarity(source, destination):
        source = StrHelper.removeAllPunctuation(source.lower())
        srcList = source.split()
        destination = StrHelper.removeAllPunctuation(destination.lower())
        destList = (destination).split()
        wDict = {}
        for w in destList:
            wDict[w] = w
        existCount = 0
        for w in srcList:
            if w in wDict:
                existCount += 1
        total = len(srcList)
        if total == 0:
            total = len(destList)
        ratio = float(existCount) / float(total)
        return int(ratio * 100)
            
    @staticmethod
    def searchOne(inputStr, pattern, default = None):
        m = re.search(pattern, inputStr)
        if (m):
            return m.group(0)
        else:
            return default

    @staticmethod
    def searchOneIgnoreCase(inputStr, pattern, default = None):
        m = re.search(pattern, inputStr, re.IGNORECASE)
        if (m):
            return m.group(0)
        else:
            return default

    @staticmethod
    def searchAll(inputStr, pattern):
        return re.findall(pattern, inputStr)
    
    @staticmethod
    def removeAllPunctuation(s):
        for c in string.punctuation:
            s = s.replace(c," ")
        return s
    
    @staticmethod
    def getLevDistance(source, destination):
        distance = pylev.levenshtein(source, destination)
        return distance
    
if __name__=="__main__":
    print("main")
    inputStr = "00000.11111.22222.33333.44444.55555.66666"
    outputStrList = StrHelper.split(inputStr, 4, '.')
    outputStrList = StrHelper.split(inputStr, 10, '.')
    outputStrList = StrHelper.split(inputStr, 30, '.')
    
    inputStr = "hello123hello"
    pattern = r"\d+"
    found = StrHelper.searchOne(inputStr, pattern)
    print (found)

    style = 'style="width: 750px; height: 744.048px; margin-left: 0px; margin-top: 0px;"'
    widthStr = StrHelper.searchOne(style, 'width:\s*\d+(\.\d+)*px')
    heightStr = StrHelper.searchOne(style, 'height:\s*\d+(\.\d+)*px')
    
    inputStr = "The Title \n by westwin simon, intel"
    pattern = r"By[\s]+[a-zA-Z\s]+"
    found = StrHelper.searchOneIgnoreCase(inputStr, pattern)
    print (found)
    
    src = "hello world, i say to him: love shanghai"
    dst = "hello world, i love shanghai and beijing"
    ratio = StrHelper.getWordSimilarity(src, dst)
    print (ratio)
    src = "hello world, i say to him: love shanghai"
    dst = "hello world, i say to him: love shanghai: by WEBMD"
    distance = StrHelper.getLevDistance(src, dst)
    print (distance)
    print (distance/len(src))
    
    
    
    print("exit")
    
    