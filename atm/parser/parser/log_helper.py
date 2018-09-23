# coding=utf-8

import datetime

class LogHelper:
    
    @staticmethod
    def log (content):
        print (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + content)

