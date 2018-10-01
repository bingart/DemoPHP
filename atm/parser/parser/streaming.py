#!/usr/bin/python
# coding=utf-8

import time
import os
import re
from os import listdir
from os.path import isfile, join
from datetime import datetime
from file_helper import FileHelper
from mongo_helper import MongoHelper
from http_helper import HttpHelper
from url_helper import UrlHelper
from parse_helper import ParseHelper

MONGO_HOST = "172.16.40.128:27017,172.16.40.140:27017,172.16.40.141:27017"
MONGO_HOST = "127.0.0.1:27017"
MONGO_DATABASE_NAME = "ZDBAmazon"
MONGO_KEY_COLLECTION = "key"
MONGO_PAGE_COLLECTION = "page"
MONGO_TRACK_COLLECTION = "track"
ROOT_PATH = 'E:/NutchData/pages/wpm'
BACKUP_PATH = 'E:/NutchData/pages/backup'

keyCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_KEY_COLLECTION, "title")
pageCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_PAGE_COLLECTION, "url")
trackCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_TRACK_COLLECTION, "url")
DOMAIN = 'http://www.infosoap.com'
QUERY_URL = 'http://www.infosoap.com/wp-content/plugins/post-api/get_post_by_title.php?token=P@ssw0rd'
INSERT_URL = 'http://www.infosoap.com/wp-content/plugins/post-api/insert_post.php?token=P@ssw0rd'
DELETE_URL = 'http://www.infosoap.com/wp-content/plugins/post-api/delete_post.php?token=P@ssw0rd'
DELI = '____'
PERMALINKS_URL = 'http://www.infosoap.com/wp-content/plugins/post-tester/get_all_permalinks.php'

def uploadPage(source):
    try:
        total = 0
        while True:
            if source == 'page':
                docList = pageCollection.nextPage(20)
            else:
                docList = keyCollection.nextPage(20)
            if docList == None or len(docList) == 0:
                break

            for doc in docList:
                if doc['state'] != 'PARSED':
                    continue

                # search wp by title
                req = {
                    'title': doc['title']
                }
                errorCode, rsp = HttpHelper.post(DOMAIN + QUERY_URL, req)
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

def downloadTrackingLog(siteName, logDate = None):
    if logDate == None:
        now = datetime.now()
        logDate = now.strftime('%Y%m%d')
    logFileName = '{0}.{1}.log'.format(siteName, logDate)
    url = 'http://:45.79.95.201/logs/{0}.{1}.log'.format(siteName, logDate)
    statusCode, html, finalUrl = HttpHelper.fetch(url)
    if statusCode == 200 and html != None and len(html) > 0:
        filePath = ROOT_PATH + '/' + logFileName
        FileHelper.writeContent(filePath, html)
        print ('download log file ok, fileName=' + logFileName)
    else:
        print ('download log file error, fileName=' + logFileName)

def importTrackingLog():
    onlyfiles = [f for f in listdir(ROOT_PATH) if isfile(join(ROOT_PATH, f))]
    for f in onlyfiles:
        lines = FileHelper.loadFileList(f)
        for line in lines:
            pList = line.split(DELI)
            if len(pList) == 4:
                trackTime = pList[0]
                trackDate = trackTime[0, 10]
                ua = pList[1]
                url = pList[2]
                uip = pList[3]

                if True:
                    old = trackCollection.queryOneByFilter({'url': url, 'trackDate': trackDate})
                    if old == None:
                        trackCollection.insertOne({
                            'url': url,
                            'trackDate': trackDate,
                            'count': 0,
                        })
                    else:
                        old['count'] = old['count'] + 1
                        trackCollection.updateOne(old)
                    
        backupFilePath = f.replace(ROOT_PATH, BACKUP_PATH)
        os.rename(f, backupFilePath)
        print ('import file, ' + f)                

def eliminatePost():
    try:
        # Filter tracking, get top 100 post page
        top100List = trackCollection.findPage({}, 0, 100, 'count', 'desc')
        
        # Get all post id and permalinks
        statusCode, html, finalUrl = HttpHelper.fetch(PERMALINKS_URL)
        if statusCode != 200 or html == None:
            print ('get all post id and permalinks fails, statusCode={0}'.format(statusCode))
        lines = html.split('\n')
        print ('get all post id and links ok, len={0}'.format(len(lines)))
        eliminateList = []
        for line in lines:
            kv = line.split(';')
            if len(kv) == 2:
                postId = kv[0]
                postLink = kv[1]
                if not postLink in top100List:
                    eliminateList.append(postId)
        
        # Remove all post not int top 100
        print ('eliminate len='.format(len(eliminateList)))
        for id in eliminateList:
            req = {
                'ID': id,
            }
            errorCode, rsp = HttpHelper.post(DELETE_URL, req)
            if errorCode != 'OK' or rsp['errorCode'] != 'OK':
                raise Exception('delete error, id={0}'.format(id))
            else:
                print ('eleminate post ok, id={0}'.format(id))
                
    except Exception as err :
        print(err)    
    
                                    
if __name__=="__main__":
    uploadPage('key')