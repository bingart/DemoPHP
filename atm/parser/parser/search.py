#!/usr/bin/python
# coding=utf-8

import time
import os
import re
import sys
from file_helper import FileHelper
from mongo_helper import MongoHelper
from http_helper import HttpHelper
from url_helper import UrlHelper
from parse_helper import ParseHelper

MONGO_HOST = "172.16.40.128:27017,172.16.40.140:27017,172.16.40.141:27017"
#MONGO_HOST = "127.0.0.1:27017"
MONGO_DATABASE_NAME = "ZDBWordPress"
MONGO_KEY_COLLECTION = "key"
MONGO_PAGE_COLLECTION = "page"
MONGO_TRACK_COLLECTION = "track"
SEARCH_KEY_PATTERN = 'http://healthtopquestions.com/wp-content/plugins/post-tester/bingapi.php?token=P@ssw0rd&t=web&q="{0}"&offset={1}&count={2}'
SEARCH_KEY_PATTERN = 'http://www.infosoap.com/wp-content/plugins/post-tester/bingapi.php?token=P@ssw0rd&t=web&q="{0}"&offset={1}&count={2}'
SEARCH_PAGE_PATTERN = 'http://healthtopquestions.com/wp-content/plugins/post-tester/bingapi.php?token=P@ssw0rd&t=web&q="{0}"%20wordpress&offset={1}&count={2}'
SEARCH_PAGE_PATTERN = 'http://www.infosoap.com/wp-content/plugins/post-tester/bingapi.php?token=P@ssw0rd&t=web&q="{0}"%20wordpress&offset={1}&count={2}'
BLACK_SITE_LIST = ['webmd.com', 'drugs.com']
ROOT_PATH = 'E:/NutchData/pages/wordpress'

keyCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_KEY_COLLECTION, "title")
pageCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_PAGE_COLLECTION, "url")
    

def loadKey():
    keyList = FileHelper.loadFileList('d:/key.txt')
    for key in keyList:
        old = keyCollection.findOneByFilter({'title': key})
        if old == None:
            keyCollection.insertOne({
                'title': key,
                'state': 'CREATED',
                'level': 0,
                'parent': None,
            })
        
def searchKeyByKey():
    try:
        total = 0
        while True:
            docList = keyCollection.findPage({'state': 'CREATED'}, 0, 20)
            if docList == None or len(docList) == 0:
                break

            for doc in docList:
                url = SEARCH_KEY_PATTERN.format(doc['title'], 0, 10)
                errorCode, response = HttpHelper.get(url)
                if errorCode != 'OK' or response == None:
                    continue

                if (not 'result' in response):
                    continue
                
                result = response['result']
                if (not 'relatedSearches' in result) \
                    or (not 'webPages' in result):
                    continue
                
                relatedSearches = result['relatedSearches']
                if not 'value' in relatedSearches:
                    continue
                
                webPages = result['webPages']
                if not 'totalEstimatedMatches' in webPages:
                    continue
                
                value = relatedSearches['value']
                newKeyList = []
                for item in value:
                    if 'text' in item:
                        newKeyList.append(item['text'])
                        
                for key in newKeyList:
                    if keyCollection.findOneByFilter({'title': key}) == None:
                        keyCollection.insertOne({
                            'title': key,
                            'state': 'CREATED',
                            'level': doc['level'] + 1,
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

# search pages by key and save into page collection
def searchPageByKey():
    try:
        total = 0
        while True:
            docList = keyCollection.findPage({'state': 'CREATED'}, 0, 20)
            if docList == None or len(docList) == 0:
                break

            for doc in docList:

                total += 1
                print ('total=' + str(total))
                
                pageList = []
                for offset in [0, 20, 40]:
                    url = SEARCH_PAGE_PATTERN.format(doc['title'], offset, 20)
                    errorCode, response = HttpHelper.get(url)
                    if errorCode != 'OK' or response == None or (not 'result' in response):
                        break
                    
                    if not 'webPages' in response['result']:
                        break
                    
                    webPages = response['result']['webPages']
                    if not 'value' in webPages:
                        break
                    
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
                            
                            isBlack = False
                            for site in BLACK_SITE_LIST:
                                if site in item['url']:
                                    isBlack = True
                                    
                            if not isBlack:
                                pageList.append(page)
                
                if len(pageList) > 0:
                    doc['pageList'] = pageList
                    doc['state'] = 'PAGED'
                    print ('search page by key, key={0}, found={1}'.format(doc['title'], len(pageList)))
                else:
                    doc['state'] = 'CLOSED'
                    print ('search page by key, key={0}, closed'.format(doc['title']))
                keyCollection.updateOne(doc)

                if len(pageList) > 0:
                    pageCollection.insertMany(pageList)

                time.sleep(1)
    
    except Exception as err :
        print(err)    

# parse page collection
def parsePage():
    try:
        total = 0
        while True:
            docList = pageCollection.findPage({'state': 'CREATED'}, 0, 20)
            if docList == None or len(docList) == 0:
                break

            for doc in docList:
                
                try:
                    total += 1
                    print ('total=' + str(total))
                    print ('url=' + doc['url'])
                    
                    fileName, finalUrl = HttpHelper.fetchAndSave(doc['url'], ROOT_PATH, 'utf-8', 2)
                    if fileName == None:
                        doc['state'] = 'CLOSED'
                        pageCollection.updateOne(doc)
                        continue
                        
                    filePath = HttpHelper.getFullPath(ROOT_PATH, fileName, 2)
                    html = FileHelper.readContent(filePath)
                    pageTitle, pageDescription, pageContent = ParseHelper.parseWordPressContent(html)
                    if pageContent != None and pageTitle != None and pageDescription != None:
                        doc['pageTitle'] = pageTitle
                        doc['pageDescription'] = pageDescription
                        doc['pageContent'] = pageContent
                        doc['state'] = 'PARSED'
                    else:
                        doc['state'] = 'CLOSED'
                    pageCollection.updateOne(doc)
    
                    time.sleep(1)
                except Exception as err :
                    print(err)
                    doc['state'] = 'CLOSED'
                    pageCollection.updateOne(doc)
    
    except Exception as err :
        print(err)
    
# Generate key page from foundList
def generateKeyPage():
    try:
        total = 0
        while True:
            docList = keyCollection.findPage({'state': 'PAGED'}, 0, 10)
            if docList == None or len(docList) == 0:
                break

            for doc in docList:
                
                total += 1
                print ('total=' + str(total))
                print ('key=' + doc['title'])
                
                foundCount = 0
                foundList = pageCollection.findPage({'key': doc['title'], 'state': 'PARSED'}, 0, 4)
                if len(foundList) == 0:
                    doc['state'] = 'CLOSED'
                    keyCollection.updateOne(doc)
                    print ('generate key page fails')
                    continue
                
                finalTitle = ''
                finalDescription = ''
                finalContent = ''
                isFirst = True
                for page in foundList:
                    title = page['title']
                    description = page['description']
                    content = page['pageContent']
                    if isFirst:
                        isFirst = False
                        finalTitle += title
                        finalDescription += description
                    else:
                        finalTitle += '; ' + title
                        finalDescription += '; ' + description
                    finalContent += '<div class="sub-content">' + content + '</div>'
                    
                    foundCount += 1
                    if foundCount >= 3:
                        break
                    
                doc['finalTitle'] = finalTitle
                doc['finalDescription'] = finalDescription
                doc['finalContent'] = finalContent
                doc['state'] = 'GENERATED'
                keyCollection.updateOne(doc)
                print ('generate key page ok')

                time.sleep(1)
    
    except Exception as err : 
        print(err)    
    
if __name__=="__main__":
    cmd = 'load'
    if len(sys.argv) == 2:
        cmd = sys.argv[1]
    else:
        cmd = 'generate'
    
    if cmd == 'load':
        loadKey()
    elif cmd == 'k2k':
        searchKeyByKey()
    elif cmd == 'k2p':
        searchPageByKey()
    elif cmd == 'parse':
        parsePage()
    #parseKey()
    elif cmd == 'generate':
        generateKeyPage()