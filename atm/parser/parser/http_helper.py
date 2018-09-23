# coding=utf-8
import requests
import hashlib
import os
import json
from log_helper import LogHelper

class HttpHelper:
    
    def __init__(self):
        LogHelper.log("created")

    @staticmethod
    def fetchWithHost(url, host, encoding="utf-8", theTimeOut=(30, 30)):
        try:
            rsp = requests.get(
                url, 
                headers={
                    'Host': host,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
                }, 
                timeout = theTimeOut, 
                allow_redirects = True,
                verify = False)
            statusCode = rsp.status_code
            html = None
            if statusCode == 200 or statusCode == 201:
                if rsp.apparent_encoding != None:
                    html = rsp.content.decode(rsp.apparent_encoding)
                else:
                    html = rsp.content.decode(encoding)

            return [statusCode, html, rsp.url]
        except Exception as err :
            print(err)
            return [407, None, None]
    
    @staticmethod
    def fetchRedirect(url, host, theTimeOut=(30, 30)):
        try:
            rsp = requests.get(
                url, 
                headers={
                    'Host': host,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
                },
                timeout = theTimeOut,
                allow_redirects = False,
                verify = False)
            statusCode = rsp.status_code
            redirectUrl = None
            if statusCode == 301 or statusCode == 302:
                redirectUrl = rsp.next.url
            return [statusCode, redirectUrl]
        except Exception as err :
            print(err)
            return [407, None]
    
    @staticmethod
    def fetch(url, encoding = "utf-8", headers = None, theTimeOut=(30, 30)):
        try:
            defaultHeaders = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            }
            if headers != None:
                defaultHeaders = headers;
                
            rsp = requests.get(url, headers=defaultHeaders, timeout=theTimeOut, allow_redirects=True)
            statusCode = rsp.status_code
            html = None
            if statusCode == 200 or statusCode == 201:
                if rsp.apparent_encoding != None:
                    html = rsp.content.decode(rsp.apparent_encoding)
                else:
                    html = rsp.content.decode(encoding)
                        
            return [statusCode, html, rsp.url]
        except Exception as err :
            print(err)
            return [407, None, None]        

    @staticmethod
    def fetchAndSave(url, rootPath, encoding = 'utf-8', prefixLen = 1):
        try:
            statusCode, html, redirectUrl = HttpHelper.fetch(url, encoding)
            if statusCode != 200:
                return None, None
            
            m = hashlib.md5()
            m.update(url.encode("utf-8"))
            fileName = m.hexdigest() + ".html"                    
            prefix = fileName[0:prefixLen]
            filePath = rootPath + "\\" + prefix
            if not os.path.exists(filePath):
                os.makedirs(filePath, 0o755);
            filePath += "\\" + fileName    
            # save html
            if html == None or len(html) <= 2048:
                return None, None
            
            with open(filePath, 'w', encoding='utf-8') as file:
                file.write(html)
            return fileName, redirectUrl
        except Exception as err :
            print(err)
            return None, None
        
    @staticmethod
    def getFullPath(rootPath, fileName, prefixLen = 1):
        prefix = fileName[0:prefixLen]
        filePath = rootPath + "/" + prefix + "/" + fileName
        return filePath

    @staticmethod
    def get(url, host = None):
        try:
            if host != None:
                theHeaders={
                    'Host': host,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
                }
            else:
                theHeaders = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
                }
            httpRsp = requests.get(url, headers=theHeaders, verify = False)
            statusCode = httpRsp.status_code
            if statusCode == 200:
                jsonBody = httpRsp.content.decode("utf-8")
                response = json.loads(jsonBody)
                return ['OK', response]
            else:
                return ['HTTP_ERROR', None]
        except Exception as err :
            print(err)
            return ['OTHER', None]

    @staticmethod
    def post(url, request, basicAuth = None, host = None):
        try:
            defaultHeaders = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
                'Content-Type': 'application/json',
            }
            if host != None:
                defaultHeaders['Host'] = host
                
            httpRsp = requests.post(url, json=request, headers=defaultHeaders, auth=basicAuth)
            statusCode = httpRsp.status_code
            if statusCode == 200:
                jsonBody = httpRsp.content.decode("utf-8")
                response = json.loads(jsonBody)
                return ['OK', response]
            else:
                return ['HTTP_ERROR', None]
        except Exception as err :
            print(err)
            return ['OTHER', None]

    @staticmethod
    def fetchImage(imageUrl, imageFilePath):
        response = requests.get(imageUrl)
        if response.status_code == 200:
            with open(imageFilePath, 'wb') as f:
                f.write(response.content)
            return len(response.content)
        else:
            return 0
    
if __name__=="__main__":
    print("main")
    
    # Test for fetch with host
    if True:
        statusCode, html, finalUrl = HttpHelper.fetchWithHost('http://172.16.40.244/', 'htqa.dev.chn.gbl')
        if statusCode == 200:
            print (html)
        
    # Test for fetch redirect
    if True:
        statusCode, redirectUrl = HttpHelper.fetchRedirect('http://198.11.169.77/r/slzox5', 'rp.westwin.com')
        if statusCode == 301 or statusCode == 302:
            print (redirectUrl)
        
    # Test for get with host
    if True:
        errorCode, rspObj = HttpHelper.get(
            'http://172.16.40.244/wp-content/plugins/post-filler/api_v4.php?&s=flu&tag=2949&is=1&iff=0&es=1&eff=0&count=6&d=0',
            'htqa.dev.chn.gbl')
        if errorCode == 'OK':
            print ('OK')
    
    print("exit")
