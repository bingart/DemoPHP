# coding=utf-8
from pymongo import MongoClient
from pymongo import ASCENDING, DESCENDING
from log_helper import LogHelper

class MongoHelper:
    
    def __init__(self, host, port, dbName, collectionName, indexName = None):
        LogHelper.log("created")
        self.host = host
        self.port = port
        self.client = MongoClient(host, port)
        self.db = self.client[dbName]
        self.collection = self.db[collectionName]
        self.indexName = indexName
        self.startId = None
        
        if self.indexName != None:
            self.collection.create_index(self.indexName)
            
    def count(self, theFilter):
        if filter == None:
            return self.collection.find(theFilter).count()
        else:
            return self.collection.count()

    def findOne(self, theId):
        return self.collection.find_one({"_id": theId})
    
    def findOneByFilter(self, theFilter):
        return self.collection.find_one(theFilter)
    
    def findPage(self, theFilter, offset, count, sortField = None, orderType = 'asc'):
        docList = []
        if sortField == None:
            cursor = self.collection.find(theFilter, skip=offset, limit=count);
        else:
            if orderType == 'asc':
                order = ASCENDING
            else:
                order = DESCENDING
            cursor = self.collection.find(theFilter, skip=offset, limit=count).sort(sortField, order);
        for doc in cursor:
            docList.append(doc)
        return docList
    
    def nextPage(self, count):
        docList = []
        if self.startId == None:
            cursor = self.collection.find({}, skip = 0, limit = count);
        else:
            cursor = self.collection.find({'_id':{"$gt": self.startId}}, skip = 0, limit = count)
            
        for doc in cursor:
            docList.append(doc)
            self.startId = doc['_id']
        return docList
    
    def resetStartId(self):
        self.startId = None
    
    def insertOne(self, doc):
        self.collection.insert_one(doc)
        
    def insertMany(self, docList):
        self.collection.insert_many(docList)
        
    def deleteOne(self, doc):
        self.collection.delete_one({'_id', doc['_id']})
        
    def updateOne(self, doc):
        theId = doc['_id']
        return self.collection.find_one_and_replace({'_id': theId}, doc)
        