# coding=utf-8

import hashlib

class CryptHelper:
    
    def __init__(self):
        print("created")
    
    @staticmethod
    def getMD5Hash(source):
        m = hashlib.md5()
        m.update(source.encode("utf-8"))
        return m.hexdigest()
    
if __name__=="__main__":
    print("main")
    dst = "hello world, i say to him: love shanghai: by WEBMD"
    md5Hash = CryptHelper.getMD5Hash(dst)
    print (md5Hash)
    print("exit")
    
    