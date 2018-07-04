# -*- coding: utf-8 -*-
# contoh data:
# entries = [
#            {
#                '_id':1,
#                'text' : [ 'lorem', 'ipsum',  'dolor' ],
#                'label': [ 'O',     'B-TIME', 'O'     ],
#                'timestamp': 2018-03-29 15:11:09.130000,
#                'type': 'bazaar'
#            },
#            {
#                '_id':2,
#                'text' : [ 'lorem', ',', 'ipsum',   'dolor'   ],
#                'label': [ 'O',     'O', 'B-PLACE', 'I-PLACE' ],
#                'timestamp': 2018-05-16 10:40:10.674000,
#                'type': 'pendidikan'
#            },
#            {
#                '_id': 3,
#                'text' : [ 'lorem',  'ipsum',  'dolor', 'sit', '?' ],
#                'label': [ 'B-NAME', 'B-TIME', 'O',     'O',   'O' ],
#                'timestamp': 2018-05-16 10:41:48.999000,
#            }
#        ]

from pymongo import MongoClient, errors
from datetime import datetime
from .adb import AbstractDB
import dateutil.parser
import os

IS_PROD = os.environ.get('IS_HEROKU', None)
DEFAULT_DATASET = 'eventdata'
DEFAULT_DB_NAME = 'datasets'

class MongoDB(AbstractDB):
    def __init__(self, config, config_name='MONGO', db_name=DEFAULT_DB_NAME, dataset=DEFAULT_DATASET):
        """
        Initialize MongoDB class implements AbstractDB.
            
        Parameters
        ----------
        config : str
            Name of config file.
        config_name : str
            Name of config identifier inside the config file. 
            Default value 'MONGO'.
        db_name : str
            Name of database in MongoDB host. Set the DEFAULT_DB_NAME 
            variable to change the default value.
        dataset : str
            Name of dataset where the data was saved. Set the 
            DEFAULT_DATASET variable to change the default value.
        """
        self.dataset = dataset
        self.db_name = db_name
        super().__init__(config)
        if IS_PROD:
            mongo_host = os.environ.get('MONGO_HOST', None)
            mongo_user = os.environ.get('MONGO_USER', None)
            mongo_pass = os.environ.get('MONGO_PASS', None)
            self.mongo = MongoClient(
                'mongodb+srv://'+mongo_user+':'+mongo_pass+'@'+mongo_host+'/'+db_name)
        else:
            if config_name in self.config:
                mongo_host = self.config[config_name]['HOST']
                mongo_port = int(self.config[config_name]['PORT'])
                if 'USER' in self.config[config_name]:
                    mongo_user = self.config[config_name]['USER']
                    mongo_pass = self.config[config_name]['PASS']
                    print('mongodb+srv://'+mongo_user+':' +
                          mongo_pass+'@'+mongo_host+'/'+db_name)
                    self.mongo = MongoClient(
                        'mongodb+srv://'+mongo_user+':'+mongo_pass+'@'+mongo_host+'/'+db_name)

                else:
                    self.mongo = MongoClient(mongo_host, mongo_port)
                # print("init mongo")
            else:
                self.mongo = None
                self._check_status()

    def _check_status(self):
        """
        Checking the status of MongoDB Client. If the setting is not found the console would print “no mongo”
        """
        if self.mongo is None:
            print("no mongo")
            raise NameError

    def putData(self, data):
        """
        Inserting one data. If there is already data with the same ID then overwrite with the new data.

        Parameters
        ---------- 
        data : object
            Data that want to be saved. Minimal contains data ID.
            Example data format:
            { '_id':'123456789' }
        """
        try:
            self.getDataset().insert_one(data)
        except errors.DuplicateKeyError:
            updateData = {'$set': data}
            self.getDataset().update_one(
                {'_id': data['_id']}, updateData)

    def getEntries(self, offset, limit):
        """
        Get the sequence of data that has offset and count limit.

        Parameters
        ----------
        offset : int
            The index where the start sequence of entries.
        limit : int
            Number of data entries to get.

        Returns
        -------
        cursor
            Sequence of data from database.
        """
        return self.getAll().skip(offset).limit(limit)

    def getAll(self):
        """
        Get all data without any boundaries.

        Returns
        -------
        cursor
            Sequence of data from database.
        """
        return self.getDataset().find()

    def getId(self, id):
        """
        Get one data with the specific ID.

        Parameters
        ----------
        id : str
            String ID of the data.

        Returns
        -------
        cursor
            Sequence of data from database.
        """
        return self.getDataset().find_one({'_id': id})

    def getTimestamp(self, id):
        """
        Get timestamp of data with the specific ID.

        Parameters
        ----------
        id : str
            String ID of the data.

        Returns
        -------
        datetime
            Timestamp of the data changes.
        """
        data = self.getId(id)
        if isinstance(data['timestamp'], datetime):
            return data['timestamp']
        else:
            return None

    def setTimestamp(self, id):
        """
        Set timestamp of data to current timestamp with the specific ID.

        Parameters
        ----------
        id : str
            String ID of the data.
        """
        updateData = {'$set': {'timestamp': datetime.now()}}
        self.getDataset().update_one(
            {'_id': id}, updateData)

    # data = {'_id':[YOUR_ID],'index':[TAG_INDEX],'tag':[TAG_NAME]}
    def setData(self, data):
        """
        Set one label in certain index from data with specific ID.

        Parameters
        ----------
        data : object
            Object contains data ID, label index, and name of label.
            Example input:
            {'_id':'123456789', 'index':9, 'tag':'B-NAME' }
        """
        updateData = {'$set': {'label.'+str(data['index']): data['tag']}}
        self.getDataset().update_one(
            {'_id': data['_id']}, updateData)

    def setType(self, id, type):
        """
        Set category of data with specific ID.

        Parameters
        ---------- 
        id : str
            String ID of the data.
        type : str
            Name of category
        """
        updateData = {'$set': {'type': type}}
        self.getDataset().update_one(
            {'_id': id}, updateData)

    def removeType(self, id):
        """
        Remove category of data with specific ID.

        Parameters
        ---------- 
        id : str
            String ID of the data.
        """
        updateData = {'$unset': {'type': 1}}
        self.getDataset().update_one(
            {'_id': id}, updateData)

    def insertTagged(self, id):
        try:
            self.mongo['status']['tagged'].insert_one({'_id': id})
        except errors.DuplicateKeyError:
            pass

    def removeTagged(self, id):
        self.mongo['status']['tagged'].remove({"_id": id})

    def getTagged(self):
        datas = []

        for data in self.mongo['status']['tagged'].find():
            datas.append(data['_id'])
        result = self.getDataset().find(
            {'_id': {'$in': datas}})
        return result

    def removeDuplicateText(self, text):
        """
        Remove all duplicate data with specific text.

        Parameters
        ---------- 
        text : str
            String full_text in data.
        """
        self.getDataset().delete_many({"full_text": text})

    def setDataset(self, dataset):
        """
        Set dataset name

        
        Parameters
        ---------- 
        dataset : str
            String name of dataset.
        """
        self.dataset = dataset

    def getDataset(self):
        """
        Get client with default dataset name

        
        Returns
        ---------- 
        MongoClient
            Mongo client with specific database name and specific dataset name.
        """
        return self.mongo[self.db_name][self.dataset]
