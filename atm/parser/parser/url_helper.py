# coding=utf-8

from urllib.parse import urljoin
from urllib.parse import urlparse

from log_helper import LogHelper

class UrlHelper:
    
    def __init__(self):
        LogHelper.log("created")
    
    @staticmethod
    def relative2abs(baseUrl, relativeUrl):
        return urljoin(baseUrl, relativeUrl)

    @staticmethod
    def getHost(url):
        result = urlparse(url)
        print (result)
        return result[1]

    @staticmethod
    def getHostPath(url):
        result = urlparse(url)
        print (result)
        return [result[1], result[2]]
    
if __name__=="__main__":
    print("main")
    
    baseUrl = "http://www.baidu.com/abc/"
    relativeUrl = "/a.html"
    absUrl = UrlHelper.relative2abs(baseUrl, relativeUrl)
    print (absUrl)
    host = UrlHelper.getHost(baseUrl)
    print (host)
    
    host, path = UrlHelper.getHostPath(baseUrl)
    print (host)
    print (path)

    print("exit")