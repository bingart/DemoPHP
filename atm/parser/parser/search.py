#!/usr/bin/python
# coding=utf-8

import time
import os
import re
from file_helper import FileHelper
from mongo_helper import MongoHelper
from http_helper import HttpHelper
from url_helper import UrlHelper
from parse_helper import ParseHelper

MONGO_HOST = "172.16.40.128:27017,172.16.40.140:27017,172.16.40.141:27017"
MONGO_DATABASE_NAME = "ZDBAmazon"
MONGO_KEY_COLLECTION = "key"
MONGO_PAGE_COLLECTION = "page"
MONGO_TARGET_COLLECTION = "target"
SEARCH_PATTERN = 'http://healthtopquestions.com/wp-content/plugins/post-tester/bingapi.php?token=P@ssw0rd&t=web&q={0}&offset={1}&count={2}'
ROOT_PATH = 'E:/NutchData/pages/wpm'

keyCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_KEY_COLLECTION, "title")
pageCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_PAGE_COLLECTION, "url")
    

def loadKey():
    keyList = []
    lineList = FileHelper.loadFileList('d:/key.txt')
    for line in lineList:
        key = line.strip()
        keyList.append(key)
    
    for key in keyList:
        old = keyCollection.findOneByFilter({'title', key})
        if old == None:
            keyCollection.insertOne({
                'title': key,
                'state': 'CREATED',
                'level': 0,
                'parent': None,
            })
        
def searchKey():
    try:
        total = 0
        while True:
            docList = keyCollection.nextPage(20)
            if docList == None or len(docList) == 0:
                break

            for doc in docList:
                if doc['state'] == 'KEYED':
                    continue
                
                url = SEARCH_PATTERN.format(doc['title'], 0, 10)
                errorCode, response = HttpHelper.get(url)
                if errorCode != 'OK' or response == None or (not 'relatedSearches' in response) or (not 'webPages' in response):
                    continue
                
                relatedSearches = response['relatedSearches']
                if not 'value' in relatedSearches:
                    continue
                
                webPages = response['webPages']
                if not 'totalEstimatedMatches' in webPages:
                    continue
                
                value = relatedSearches['value']
                newKeyList = []
                for item in value:
                    if 'text' in item:
                        newKeyList.append(item['text'])
                        
                for key in newKeyList:
                    if keyCollection.queryOneByFilter({'title': key}) == None:
                        keyCollection.insertOne({
                            'title': key,
                            'state': 'CREATED',
                            'level': doc['level'],
                            'parent': doc['title'],
                            'matched': webPages['totalEstimatedMatches']
                        })

                doc['state'] = 'KEYED'
                keyCollection.updateOne(doc)
                
                total += 1
                print ('total=' + str(total))
                
                time.sleep(1)
    
    except Exception as err :
        print(err)    

def searchPage():
    try:
        total = 0
        while True:
            docList = keyCollection.nextPage(20)
            if docList == None or len(docList) == 0:
                break

            for doc in docList:
                if doc['state'] == 'PAGED':
                    continue
                
                pageList = []
                for offset in [0, 20, 40]:
                    url = SEARCH_PATTERN.format(doc['title'], offset, 20)
                    errorCode, response = HttpHelper.get(url)
                    if errorCode != 'OK' or response == None or (not 'webPages' in response):
                        continue
                    
                    webPages = response['webPages']
                    if not 'value' in webPages:
                        continue
                    
                    value = webPages['value']
                    for item in value:
                        if 'name' in item and 'url' in item and 'snippet' in item:
                            page = {
                                'title': item['name'],
                                'url': item['url'],
                                'description': item['snippet'],
                                'state': 'CREATED',
                                'key': doc['title']
                            }
                
                if len(pageList) > 0:
                    insertList = []
                    for page in pageList:
                        old = pageCollection.queryOneByFilter({'url', page['url']})
                        if old == None:
                            insertList.append(page)
                    
                    pageCollection.insertMany(insertList)
                    
                    doc['pageList'] = pageList
                    doc['state'] = 'PAGED'
                    keyCollection.updateOne(doc)

                total += 1
                print ('total=' + str(total))
                
                time.sleep(1)
    
    except Exception as err :
        print(err)    

def parsePage():
    try:
        total = 0
        while True:
            docList = pageCollection.nextPage(20)
            if docList == None or len(docList) == 0:
                break

            for doc in docList:
                if doc['state'] == 'PARSED':
                    continue

                fileName, finalUrl = HttpHelper.fetchAndSave(doc['url'], ROOT_PATH, 'utf-8', 2)
                if fileName == None:
                    doc['state'] = 'CLOSED'
                    pageCollection.updateOne(doc)
                    continue
                    
                filePath = HttpHelper.getFullPath(ROOT_PATH, fileName, 2)
                html = FileHelper.readContent(filePath)
                pageTitle, pageDescription, content = ParseHelper.parseWordPressContent(html)
                if content != None:
                    doc['pageTitle'] = pageTitle
                    doc['pageDescription'] = pageDescription
                    doc['content'] = content
                    doc['state'] = 'PARSED'
                else:
                    doc['state'] = 'CLOSED'
                pageCollection.updateOne(doc)

                total += 1
                print ('total=' + str(total))
                
                time.sleep(1)
    
    except Exception as err :
        print(err)    
    

if __name__=="__main__":
    loadKey()
    searchKey()
    searchPage()
    parsePage()