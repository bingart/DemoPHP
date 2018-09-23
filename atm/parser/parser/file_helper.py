# coding=utf-8

import hashlib
import os
import logging

class FileHelper:
    
    def __init__(self):
        logging.log("created")
    
    @staticmethod
    def readContent(filePath, encoding='utf-8'):
        with open(filePath, 'r', encoding=encoding) as f:
            content = f.read()
        f.closed
        return content
        
    @staticmethod
    def writeContent(filePath, content):
        file = open(filePath, 'w', encoding='utf-8')
        try:
            file.write(content)
        except Exception as err :
            print(err)
        finally:
            file.close()

    @staticmethod
    def writeBinary(filePath, content):
        outFile = open(filePath, "wb")
        outFile.write(content)
        outFile.close()
        
    @staticmethod
    def saveFileList(filePath, lineList, mode='w'):
        file = open(filePath, mode, encoding='utf-8')
        for line in lineList:
            try:
                file.write("%s\n" % line)
            except Exception as err :
                print(err)
        file.close()
    
    @staticmethod
    def loadFileList(filePath, encoding='utf-8'):
        lineList = []
        with open(filePath, 'r', encoding=encoding) as file:
            for line in file:
                if line in lineList:
                    print ('line ignored, line=' + line)
                else:
                    lineList.append(line.strip())
        file.close()
        # print ("size of urlList=" + str(len(lineList)))
        return lineList

    @staticmethod
    def writeHash(url, html, encoding, rootPath):
        try:
            m = hashlib.md5()
            m.update(url.encode(encoding))
            fileName = m.hexdigest() + ".html"                    
            prefix = fileName[0:1]
            filePath = rootPath + "\\" + prefix
            if not os.path.exists(filePath):
                os.makedirs(filePath, 0o755);
            filePath += "\\" + fileName    
            # save html
            if html == None or len(html) <= 2048:
                return None
            
            with open(filePath, 'w', encoding='utf-8') as file:
                file.write(html)
            return fileName
        except Exception as err :
            print(err)
            return None
        
    @staticmethod
    def readHash(fileName, theEncoding, rootPath):
        try:
            prefix = fileName[0:1]
            filePath = rootPath + "\\" + prefix + "\\" + fileName
            with open(filePath, 'r', encoding=theEncoding) as file:
                content = file.read()
                return content
        except Exception as err :
            print(err)
            return None
        

        
    