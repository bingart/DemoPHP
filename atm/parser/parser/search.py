#!/usr/bin/python
# coding=utf-8

import time
import os
import re
from file_helper import FileHelper
from mongo_helper import MongoHelper
from http_helper import HttpHelper
from url_helper import UrlHelper

MONGO_HOST = "172.16.40.128:27017,172.16.40.140:27017,172.16.40.141:27017"
MONGO_DATABASE_NAME = "ZDBAmazon"
MONGO_KEY_COLLECTION = "key"
MONGO_PAGE_COLLECTION = "page"
MONGO_TARGET_COLLECTION = "target"
SEARCH_PATTERN = 'http://healthtopquestions.com/wp-content/plugins/post-tester/bingapi.php?token=P@ssw0rd&t=web&q={0}&offset={1}&count={2}'

def loadKey():
    keyList = []
    lineList = FileHelper.loadFileList('d:/key.txt')
    for line in lineList:
        key = line.strip()
        keyList.append(key)
    
    collection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_KEY_COLLECTION, "title")
    for key in keyList:
        old = collection.findOneByFilter({'title', key})
        if old == None:
            collection.insertOne({
                'title': key,
                'state': 'CREATED',
                'level': 0,
                'parent': None,
            })
        
def searchKey():
    keyCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_KEY_COLLECTION, "title")
    
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
                if errorCode != 'OK' or response == None or (not 'relatedSearches' in response):
                    continue
                
                relatedSearches = response['relatedSearches']
                if not 'value' in relatedSearches:
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
                            'parent': doc['title']
                        })

                doc['state'] = 'KEYED'
                keyCollection.updateOne(doc)
                
                total += 1
                print ('total=' + str(total))
                
                time.sleep(1)
    
    except Exception as err :
        print(err)    

def searchPage():
    keyCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_KEY_COLLECTION, "title")
    pageCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_PAGE_COLLECTION, "url")
    
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
                
                for offset in [0, 20]:
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
                    for page in pageList:
                        if pageCollection.queryOneByFilter({'url': page['url']}) == None:
                            pageCollection.insertOne(page)
    
                    doc['state'] = 'PAGED'
                    keyCollection.updateOne(doc)

                total += 1
                print ('total=' + str(total))
                
                time.sleep(1)
    
    except Exception as err :
        print(err)    

if __name__=="__main__":
    loadKey()
    searchKey()
    searchPage()