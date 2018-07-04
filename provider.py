from database.md import MongoDB
from configparser import ConfigParser
import datetime
import dateparser
import pymysql

CONFIG_FILE = 'config.ini'

class DataProvider(object):
    def __init__(self, config=CONFIG_FILE, mapClient=None):
        """
        Initialize DataProvider class implements object.
            
        Parameters
        ----------
        config : str
            Name of config file. Default value is config.ini
        mapClient : googlemaps.Client
            Client for using googlemaps API. Default value is None.
        """
        self.gmaps = mapClient
        self.md = MongoDB(config)
        self.config = ConfigParser()
        self.config.read(config)

    def setMapClient(self, mapClient):
        """
        Set client for googlemaps API
            
        Parameters
        ----------
        mapClient : googlemaps.Client
            Client for using googlemaps API. Default value is None.
        """
        self.gmaps = mapClient
    
    def connect(self):
        """
        Connecting to MySQL host based on the initialized configuration file. Should be called once when start using the database.
        """
        self.conn = pymysql.connect(
            host = self.config['DB']['HOST'],
            user = self.config['DB']['USER'],
            passwd = self.config['DB']['PASSWORD'],
            db = self.config['DB']['NAME'],
            use_unicode=True, 
            charset="utf8mb4"
        )
 
    def disconnect(self):
        """
        Disconnecting from MySQL host. Should be called once in the end after using the database.
        """
        self.conn.close()

    def _make_entities(self, data, save):
        extracted = self.extractText(
            data['label'],
            data['text']
        )
        data['entities'] = {}
        name = []
        places = []
        time = []
        info = []

        if extracted is None:
            return None

        for d in extracted:
            label = d['label']
            ok = self.parserEvent(label, d['text'], data['created_time'])
            if ok is not None:
                if label == 'NAME':
                    name.append(ok)
                elif label == 'PLACE':
                    for k in ok:
                        places.append(k)
                elif label == 'TIME':
                    time.append(ok)
                else:
                    info.append(ok)

        if len(name) > 0:
            data['entities']['name'] = name
        if len(places) > 0:
            data['entities']['place'] = self.removeDuplicate(
                places, key='location'
            )
        if len(time) > 0:
            data['entities']['time'] = time
        if len(info) > 0:
            data['entities']['info'] = info

        if data['entities'] == {}:
            return None
        # print(data)
        if save:
            self.md.putData(data)
        return data

    def makeData(self, refresh=False):
        """
        Make all entities for every data in database. Print all the successfull generated entities data.

        Parameters
        ----------
        refresh : boolean
            if false then generate only when entities key in data is not exist.
            if true then generate all data ignore the existance of entities key. 
            Default value is false.

        """
        for d in self.md.getAll():
            if 'entities' not in d.keys() or refresh:
                data = self._make_entities(d, True)
                if data is not None:
                    print(data['entities'])

    def getData(self, id, save=False):
        """
        Get one data with the specific ID and adding one new key as entities that processed by the function.

        Parameters
        ----------
        id : str
            String ID of the data.
        save : boolean
            if true then save the new data generated. 
            Default value is false.

        Returns
        -------
        dict
            Data from database added with entities key value.

        """
        data = self.md.getId(id)
        return self._make_entities(data, save)

    def extractText(self, labels, text):
        """
        Process sequence of labels and texts to extract important label only.

        Parameters
        ----------
        labels : list
            List of labels
        text : list
            List of text tokens 
            
        Returns
        -------
        list
            List of detected important labeled text from parameter 
            Example:
            [{'label': 'NAME', 'text': ['lorem','ipsum','dolor']},
            {'label': 'PLACE', 'text': ['Jl.','ipsum','95']}]
        """
        entities = []
        entity_name = None
        entity = []
        for index, label in enumerate(labels):
            if label[:1] == 'B':
                if entity_name is not None:
                    data = {'label': entity_name, 'text': entity}
                    entities.append(data)
                entity = []
                entity_name = label[2:]
                entity.append(text[index])
            elif label[:1] == 'I' and label[2:] == entity_name:
                entity.append(text[index])
            elif label[:1] == 'O':
                if entity_name is not None:
                    data = {'label': entity_name, 'text': entity}
                    entities.append(data)
                entity_name = None
                entity = []
        return self.removeDuplicate(entities)

    def removeDuplicate(self, old_list, key='text'):
        """
        Remove any duplication of dict inside a list

        Parameters
        ----------
        old_list : list
            List of dicts
        key : str
            Key of the dict that the value is identified as unique

        Returns
        -------
        list
            New list without duplicated dict
        """
        if len(old_list) < 2:
            return old_list
        seen = set()
        new_list = []
        for d in old_list:
            t = tuple(d[key])
            if t not in seen:
                seen.add(t)
                new_list.append(d)
        return new_list

    def parserEvent(self, label, array, created):
        """
        Parse token based on its label

        Parameters
        ----------
        label : str
            Name of label
        array : list
            List of tokens

        Returns
        -------
        str/list/datetime
            If the label is TIME then return datetime if the label is PLACE then return list of dict else parsed form of token as one whole string
        """
        text = " ".join(array)
        if label == 'TIME':
            return self.time_process(
                text,
                created
            )
        if label == 'PLACE':
            return self.place_process(text)
        return text
        
    def time_process(self, text, created):
        """
        Parse string into datetime

        Parameters
        ----------
        text : str
            String to parse
        created : datetime
            Date relative to the parsed text

        Returns
        -------
        datetime
            Datetime of the result of parsing process
        """
        return dateparser.parse(text, settings={'RELATIVE_BASE':created})

    def place_process(self, text):
        """
        Query string to get list of places based on search feature from google place API.

        Parameters
        ----------
        text : str
            String to query

        Returns
        -------
        list
            List of dict with place information that
        """
        if self.gmaps is None:
            return [{'name':text, 'address':text, 'location':{'lat':None,'lng':None}}]
            
        data = self.gmaps.places(query=text)
        entities = []
        for d in data['results']:
            location = d['geometry']['location']
            name = d['name']
            address = d['formatted_address']
            entity = {'name': name, 'address': address, 'location': location}
            entities.append(entity)
        return entities

if __name__ == '__main__':
    a = DataProvider()
    data = a.getData('999998633956265985')
    print(data)
