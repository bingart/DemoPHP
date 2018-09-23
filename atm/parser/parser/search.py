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
                'refer': None,
            })
        
def searchKey():
    keyCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_KEY_COLLECTION, "title")
    pageCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_KEY_COLLECTION, "url")
    
    try:
        total = 0
        while True:
            docList = keyCollection.nextPage(20)
            if docList == None or len(docList) == 0:
                break

            for doc in docList:
                if doc['state'] == 'COMPLETED':
                    continue
                
                
                
                total += 1
                print ('total=' + str(total))
                
                time.sleep(1)
    
    except Exception as err :
        print(err)    

if __name__=="__main__":
    loadKey()
    searchKey()