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
ROOT_PATH = 'E:/NutchData/pages/wpm'

keyCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_KEY_COLLECTION, "title")
pageCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_PAGE_COLLECTION, "url")
targetCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_TARGET_COLLECTION, "url")
QUERY_URL = 'http://healthtopquestions.com/wp-content/plugins/post-api/get_post_by_title.php?token=P@ssw0rd'
INSERT_URL = 'http://healthtopquestions.com/wp-content/plugins/post-api/insert_post.php?token=P@ssw0rd'

def parsePage():
    try:
        total = 0
        while True:
            docList = pageCollection.nextPage(20)
            if docList == None or len(docList) == 0:
                break

            for doc in docList:
                if doc['state'] != 'PARSED':
                    continue

                # search wp by title
                req = {
                    'title': doc['title']
                }
                errorCode, rsp = HttpHelper.post(QUERY_URL, req)
                if errorCode != 'OK':
                    raise Exception('query error, url=' + doc['url'])
                if rsp['errorCode'] == 'ERROR':
                    doc['state'] = 'DUPED'
                    pageCollection.updateOne(doc)
                    continue
                
                # upload
                postTitle = doc['pageTitle']
                if postTitle == None:
                    postTitle = doc['title']
                postExcerpt = doc['pageDescription']
                if postExcerpt == None:
                    postExcerpt = doc['description']
                req = {
                    'ID': 0,
                    'author': 1,
                    'title': postTitle,
                    'excerpt': postExcerpt,
                    'content': doc['content'],
                    'categories': [1]
                }
                errorCode, rsp = HttpHelper.post(INSERT_URL, req)
                if errorCode != 'OK':
                    raise Exception('insert error, url=' + doc['url'])

                if rsp['errorCode'] == 'ERROR':
                    doc['state'] = 'POSTERROR'
                else:
                    doc['state'] = 'POSTED'
                pageCollection.updateOne(doc)

                total += 1
                print ('total=' + str(total))
                
                time.sleep(1)
    
    except Exception as err :
        print(err)    
    

if __name__=="__main__":
    parsePage()