#!/usr/bin/python
# coding=utf-8

import time
import os
import re
import sys
from os import listdir
from os.path import isfile, join
from datetime import datetime, timedelta
from file_helper import FileHelper
from mongo_helper import MongoHelper
from http_helper import HttpHelper
from url_helper import UrlHelper
from parse_helper import ParseHelper

MONGO_HOST = "172.16.40.128:27017,172.16.40.140:27017,172.16.40.141:27017"
MONGO_HOST = "127.0.0.1:27017"
MONGO_DATABASE_NAME = "ZDBWordPress"
MONGO_KEY_COLLECTION = "key"
MONGO_PAGE_COLLECTION = "page"
MONGO_TRACK_COLLECTION = "track"
LOGS_PATH = 'E:/NutchData/Traffic/logs'
BACKUP_PATH = 'E:/NutchData/Traffic/backup'
PERMALINKS_PATH = 'E:/NutchData/Traffic/permalinks'

if not os.path.exists(LOGS_PATH):
    os.makedirs(LOGS_PATH, exist_ok=True)
if not os.path.exists(BACKUP_PATH):
    os.makedirs(BACKUP_PATH, exist_ok=True)
if not os.path.exists(PERMALINKS_PATH):
    os.makedirs(PERMALINKS_PATH, exist_ok=True)

keyCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_KEY_COLLECTION, "title")
pageCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_PAGE_COLLECTION, "url")
trackCollection = MongoHelper(MONGO_HOST, 27017, MONGO_DATABASE_NAME, MONGO_TRACK_COLLECTION, "url")
trackCollection.createIndex('trackDate')
QUERY_URL = 'http://www.infosoap.com/wp-content/plugins/post-api/get_post_by_title.php?token=P@ssw0rd'
DELETE_URL = 'http://www.infosoap.com/wp-content/plugins/post-api/delete_post.php?token=P@ssw0rd'
DELI = '____'
PERMALINKS_URL = 'http://www.infosoap.com/wp-content/plugins/post-tester/get_all_permalinks.php?offset={0}&limit={1}'


def downloadTrackingLog(siteName, logDate = None):
    if logDate == None:
        now = datetime.now() - timedelta(days=1)
        logDate = now.strftime('%Y%m%d')
    logFileName = '{0}.{1}.log'.format(siteName, logDate)
    url = 'http://45.79.95.201/logs/{0}.{1}.log'.format(siteName, logDate)
    statusCode, html, finalUrl = HttpHelper.fetch(url)
    if statusCode == 200 and html != None and len(html) > 0:
        filePath = LOGS_PATH + '/' + logFileName
        FileHelper.writeContent(filePath, html)
        print ('download log file ok, fileName=' + logFileName)
    else:
        print ('download log file error, fileName=' + logFileName)

def importTrackingLog():
    onlyfiles = [f for f in listdir(LOGS_PATH) if isfile(join(LOGS_PATH, f))]
    for f in onlyfiles:
        logFilePath = LOGS_PATH + '/' + f
        lines = FileHelper.loadFileList(logFilePath)
        for line in lines:
            pList = line.split(DELI)
            if len(pList) == 4:
                trackDateTime = pList[0]
                trackDate = trackDateTime[0:10]
                ua = pList[1]
                url = pList[2]
                uip = pList[3]

                if '?atr=1' in url:
                    print ('bot url, ignored, url=' + url)
                    continue

                if True:
                    # The url used will be saved forever
                    # The url used by search engine will be saved forever
                    old = trackCollection.findOneByFilter({'url': url})
                    if old == None:
                        trackCollection.insertOne({
                            'url': url,
                            'trackDate': trackDate,
                            'ua': ua,
                            'uip': uip,
                            'count': 1,
                        })
                    else:
                        old['count'] = old['count'] + 1
                        old['trackDate'] = trackDate
                        old['ua'] = ua
                        old['uip'] = uip
                        trackCollection.updateOne(old)
                    
        backupFilePath = BACKUP_PATH + '/' + f
        os.replace(logFilePath, backupFilePath)
        print ('import file, ' + f)                

def comparePost():
    try:
        # Filter tracking, get top 100 post page
        top100List = trackCollection.findPage({}, 0, 500, 'count', 'desc')
        top100Dict = {}
        for doc in top100List:
            top100Dict[doc['url']] = ''
            
        # Get all post id and permalinks
        eliminateIdList = []
        eliminateLinkList = []
        for offset in range(0, 6000, 100):
            url = PERMALINKS_URL.format(offset, 100)
            statusCode, html, finalUrl = HttpHelper.fetch(url)
            if statusCode != 200 or html == None:
                print ('get all post id and permalinks fails, statusCode={0}'.format(statusCode))
                break
            lines = html.split('\n')
            print ('get all post id and links ok, len={0}'.format(len(lines)))
            postCount = 0
            for line in lines:
                kv = line.split(';')
                if len(kv) == 2:
                    postCount += 1
                    postId = kv[0]
                    postLink = kv[1]
                    if not postLink in top100Dict:
                        eliminateIdList.append(postId)
                        eliminateLinkList.append(line)
            
            if postCount <= 0:
                print ('################# offset={0}, break'.format(offset))
                break
            else:
                print ('################# offset={0}, ok'.format(offset))
        permalinksIdFilePath = PERMALINKS_PATH + '/id.txt'    # TODO
        permalinksLinkFilePath = PERMALINKS_PATH + '/link.txt'    # TODO
        FileHelper.saveFileList(permalinksIdFilePath, eliminateIdList)
        FileHelper.saveFileList(permalinksLinkFilePath, eliminateLinkList)

    except Exception as err :
        print(err)    

def deletePost():
    try:
        permalinksIdFilePath = PERMALINKS_PATH + '/id.txt'
        eliminateIdList = FileHelper.loadFileList(permalinksIdFilePath)
        print ('eliminate len={0}'.format(len(eliminateIdList)))
        for postID in eliminateIdList:
            req = {
                'ID': int(postID),
            }
            errorCode, rsp = HttpHelper.post(DELETE_URL, req)
            if errorCode != 'OK' or rsp['errorCode'] != 'OK':
                print ('delete post error, ID={0}'.format(postID))
            else:
                print ('delete post ok, ID={0}'.format(postID))
                
    except Exception as err :
        print(err)    
    
def generateTaskList():
    try:    
        # Get all post id and permalinks
        eliminateLinkList = []
        for offset in range(0, 6000, 100):
            url = PERMALINKS_URL.format(offset, 100)
            statusCode, html, finalUrl = HttpHelper.fetch(url)
            if statusCode != 200 or html == None:
                print ('get all post id and permalinks fails, statusCode={0}'.format(statusCode))
                break
            lines = html.split('\n')
            print ('get all post id and links ok, len={0}'.format(len(lines)))
            postCount = 0
            for line in lines:
                kv = line.split(';')
                if len(kv) == 2:
                    postCount += 1
                    postId = kv[0]
                    postLink = kv[1]
                    eliminateLinkList.append(postLink + '?atr=1')
            
            if postCount <= 0:
                print ('################# offset={0}, break'.format(offset))
                break
            else:
                print ('################# offset={0}, ok'.format(offset))
        FileHelper.saveFileList('./task.infosoap.txt', eliminateLinkList)

    except Exception as err :
        print(err)    

                 
if __name__=="__main__":

    cmd = 'upload'
    if len(sys.argv) == 2:
        cmd = sys.argv[1]
    else:
        cmd = 'delete'
    
    if cmd == 'download':
        downloadTrackingLog('diabetes')
    elif cmd == 'import':
        importTrackingLog()
    elif cmd == 'compare':
        comparePost()
    elif cmd == 'delete':
        deletePost()
    elif cmd == 'task':
        generateTaskList()
    else:
        print ('unknown cmd={0}'.format(cmd))
        