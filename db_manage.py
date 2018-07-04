from database.md import MongoDB
from mongo import MongoProvider
from provider import DataProvider
import googlemaps

def main():
    gmaps = googlemaps.Client(key='AIzaSyC9Jw099A_9uXyK8KFQPxR93-cg3ks5E40')
    p = DataProvider(mapClient=gmaps)
    p.makeData(refresh=False)

def main1():
    db = MongoProvider('config.ini')
    data = db.getAllPlace()
    print('PLACE', data.length)
    data = db.getAllTime()
    print('TIME', data.length)

if __name__ == '__main__':
    main()
