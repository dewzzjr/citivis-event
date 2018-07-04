from database.md import MongoDB
import pymongo

class MongoProvider(MongoDB):

    def getAllPlace(self):
        return self.getAll().distinct('entities.place')

    def getAllTime(self):
        return self.getAll().distinct('entities.time')

    def searchEventsByLocation(self, data):
        return self.mongo[self.db_name][self.dataset].find(
            {'entities.place': {'$in': [data]}}
        ).sort([("created_time", pymongo.DESCENDING)]).limit(15)
