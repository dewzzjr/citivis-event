from database.md import MongoDB
import datetime
import pymongo

class MongoProvider(MongoDB):
    def getAll(self):
        return self.getDataset().find().sort("created_time", pymongo.DESCENDING)

    def getAllPlace(self):
        return self.getAll().distinct('entities.place')

    def getAllTime(self):
        return self.getAll().distinct('entities.time')

    def searchEventsByLocation(self, data):
        return self.getDataset().find(
            {'entities.place': {'$in': [data]}}
        ).sort([("created_time", pymongo.DESCENDING)]).limit(30)
    
    def searchEventsByTime(self, data):
        return self.getDataset().find(
            {'entities.time': {'$in': [data]}}
        ).sort([("created_time", pymongo.DESCENDING)])

    def searchEventsByUpcoming(self):
        data = datetime.datetime.today()
        return self.getDataset().find(
            {
                'entities.time': {'$gte': data}
            }
        ).sort([("created_time", pymongo.DESCENDING)])
