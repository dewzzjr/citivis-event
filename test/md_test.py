import unittest
import datetime
import database.md
import mongo

class ExtensionMongoTestCase(unittest.TestCase):
    def setUp(self):
        self.d = mongo.MongoProvider('config.ini')

    def test_search_by_loc(self):
        data = {
            "name": "Grand City Mall Surabaya",
            "address": "Jalan Walikota Mustajab No. 1, Ketabang, Genteng, Kota SBY, Jawa Timur 60272, Indonesia",
            "location": {
                "lat": -7.2615135,
                "lng": 112.7505606
            }
        }
        result = self.d.searchEventsByLocation(data)
        
        self.assertGreater(result.count(), 0)
        # for i in result:
        #     print(i)

# SKENARIO 104
class RemoveDuplicateTestCase(unittest.TestCase):
    def setUp(self):
        self.d = database.md.MongoDB('config.ini', dataset='test')

    def tearDown(self):
        self.d.mongo[self.d.db_name].drop_collection(self.d.dataset)

    def test_remove(self):
        # print('PUT DATA - COUNT DATA - REMOVE DUP - COUNT DATA')
        date = datetime.datetime(2011, 2, 3, 10, 11)
        ids = ['111','222','333','444']
        data = {
            '_id': '000',
            'full_text': 'lorem ipsum dolor',
            'text' : [ 'lorem', 'ipsum',  'dolor' ],
            'label': [ 'O',     'B-TIME', 'O'],
            'timestamp': date,
            'type': 'bazaar'
        }
        for id in ids:
            self.d.putData(data)
            data['_id'] = id
        removedText = data['full_text']
        data['full_text'] = 'lorem ipsum dolor new'
        self.d.putData(data)

        expect = 5
        result = self.d.getAll().count()
        self.assertEqual(result, expect)

        self.d.removeDuplicateText(removedText)
        expect = 1
        result = self.d.getAll().count()
        self.assertEqual(result, expect)

# SKENARIO 102
class PutMongoTestCase(unittest.TestCase):
    def setUp(self):
        self.d = database.md.MongoDB('config.ini', dataset='test')

    def tearDown(self):
        self.d.mongo[self.d.db_name].drop_collection(self.d.dataset)

    def test_put_data_0(self):
        # print('PUT DATA - GET ID - GET TIMESTAMP')
        date = datetime.datetime(2011, 2, 3, 10, 11)
        id = '111'
        expect = {
            '_id': id,
            'text' : [ 'lorem', 'ipsum',  'dolor' ],
            'label': [ 'O',     'B-TIME', 'O'     ],
            'timestamp': date,
            'type': 'bazaar'
        }
        self.d.putData(expect)
        result = self.d.getId(id)
        self.assertEqual(result, expect)
        
        stamp = self.d.getTimestamp(id)
        self.assertEqual(stamp, date)

    def test_put_data_1(self):
        # print('PUT DATA - GET DATA - PUT DATA - GET ID')
        date = datetime.datetime(2011, 2, 3, 10, 11)
        id = '111'
        first = {
            '_id': id,
            'text' : ['lorem', 'ipsum',  'dolor'],
            'label': ['O',     'B-TIME', 'O'],
            'timestamp': date,
            'type': 'bazaar'
        }
        expect = {
            '_id': id,
            'text' : ['lorem', 'ipsum',  'dolor', 'edited'],
            'label': ['O',     'B-TIME', 'O',     'O'],
            'timestamp': date,
            'type': 'edited'
        }
        self.d.putData(first)
        result = self.d.getId(id)
        self.assertEqual(result, first)

        self.d.putData(expect)
        result = self.d.getId(id)
        self.assertEqual(result, expect)

        count = self.d.getAll().count()
        self.assertEqual(count, 1)

    def test_put_data_2(self):
        # print('PUT DATA x3 - GET ENTRIES')
        entries = [
            {
                '_id':'111',
                'text' : [ 'lorem', 'ipsum',  'dolor' ],
                'label': [ 'O',     'B-TIME', 'O'     ],
                'timestamp': datetime.datetime(2018, 3, 29, 15, 11, 9),
                'type': 'bazaar'
            },
            {
                '_id':'222',
                'text' : [ 'lorem', ',', 'ipsum',   'dolor'   ],
                'label': [ 'O',     'O', 'B-PLACE', 'I-PLACE' ],
                'timestamp': datetime.datetime(2018, 5, 16, 10, 40, 10),
                'type': 'pendidikan'
            },
            {
                '_id': '333',
                'text' : [ 'lorem',  'ipsum',  'dolor', 'sit', '?' ],
                'label': [ 'B-NAME', 'B-TIME', 'O',     'O',   'O' ],
                'timestamp': datetime.datetime(2018, 5, 16, 10, 41, 48),
            }
        ]
        for entry in entries:
            self.d.putData(entry)
        result = self.d.getEntries(1,2)
        self.assertEqual(result.count(True), 2)
        self.assertEqual(list(result), entries[1:3])
        
# SKENARIO 101
class GetMongoTestCase(unittest.TestCase):
    def setUp(self):
        self.d = database.md.MongoDB('config.ini')

    def test_get_id(self):
        # print('GET ID: 999998633956265985')
        id = '999998633956265985'

        expect = {'_id': '999998633956265985', 'source': 'tw', 'page': 'eventsurabaya',
        'created_time': datetime.datetime(2018, 5, 25, 13, 0, 28),
        'source_url': 'https://twitter.com/eventsurabaya/status/998472224305594369/photo/1',
        'image_url': 'http://pbs.twimg.com/media/DdtJDS6UQAA6uDr.jpg',
        'text': [
            'Mari', 'kita', 'umat', 'kristen', 'bersatu', 'untuk', 'berdoa', 'bagi', 'kesejahteraan', 'Indonesia', 'dalam', 'acara', 'Jesus', 'Reigns', '!', 'PARADE', ',', 'PRAISE', ',', 'PRAY.', 'Jumat', ',', '1', 'Juni', '2018', 'at', 'The', 'Square', 'Ballroom', '(', 'Basuki', 'Rahmat', '16-18', ')', '|', 'IG', 'JesusReignsIndonesia', '/', 'WA', ':', '083875757595', 'https', ':', '//t.co/1QtS43tkXW'
        ],
        'label': [
            'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-TIME', 'I-TIME', 'I-TIME', 'O', 'B-PLACE', 'I-PLACE', 'I-PLACE', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'B-INFO', 'I-INFO', 'I-INFO', 'I-INFO', 'I-INFO', 'I-INFO'
        ],
        'timestamp': datetime.datetime(2018, 5, 29, 5, 37, 41, 835000), 'entities': {
            'time': [datetime.datetime(2018, 6, 1, 0, 0)],
            'place': [{'name': 'The Square Ballroom', 'address': 'ICBC Center L3, Jl. Basuki Rahmat 16-18, Kedungdoro, Tegalsari, Kota SBY, Jawa Timur 60261, Indonesia', 'location': {'lat': -7.2646499, 'lng': 112.7407103}}]
            }
        }
        result = self.d.getId(id)

        self.assertEqual(expect['_id'], id)
        self.assertEqual(expect['label'], result['label'])
        self.assertEqual(expect['text'],  result['text'])
        self.assertEqual(expect['created_time'], result['created_time'])
        self.assertEqual(expect['source_url'],   result['source_url'])
        self.assertEqual(expect['image_url'],    result['image_url'])

# SKENARIO 103
class SetMongoTestCase(unittest.TestCase):
    
    def setUp(self):
        self.d = database.md.MongoDB('config.ini', dataset='test')
        entries = [
            {
                '_id': '111',
                'text': ['lorem', 'ipsum',  'dolor'],
                'label': ['O',     'B-TIME', 'O'],
                'timestamp': datetime.datetime(2018, 3, 29, 15, 11, 9),
                'type': 'bazaar'
            },
            {
                '_id': '222',
                'text': ['lorem', ',', 'ipsum',   'dolor'],
                'label': ['O',     'O', 'B-PLACE', 'I-PLACE'],
                'timestamp': datetime.datetime(2018, 5, 16, 10, 40, 10),
                'type': 'pendidikan'
            },
            {
                '_id': '333',
                'text': ['lorem',  'ipsum',  'dolor', 'sit', '?'],
                'label': ['B-NAME', 'B-TIME', 'O',     'O',   'O'],
                'timestamp': datetime.datetime(2018, 5, 16, 10, 41, 48),
            }
        ]
        for entry in entries:
            self.d.putData(entry)

    def tearDown(self):
        self.d.mongo[self.d.db_name].drop_collection(self.d.dataset)

    def test_set_data_0(self):
        id = '111'
        data = {'_id': id, 'index': 1, 'tag': 'B-NAME'}
        self.d.setData(data)
        result = self.d.getId(id)
        self.assertEqual(result['label'][data['index']], data['tag'])
    
    def test_set_data_1(self):
        id = '111'
        data = {'_id': id, 'nokey': None}
        with self.assertRaises(KeyError):
            self.d.setData(data)
            
    def test_set_data_2(self):
        data = {'nokey': None}
        with self.assertRaises(KeyError):
            self.d.setData(data)

    def test_set_type_0(self):
        id = '222'
        type = 'testing'
        self.d.setType(id, type)
        result = self.d.getId(id)
        self.assertEqual(result['type'], type)

    def test_set_type_1(self):
        id = '222'
        type = 'testing'
        self.d.setType(id, type)
        result = self.d.getId(id)
        self.assertEqual(result['type'], type)

        self.d.removeType(id)
        result = self.d.getId(id)
        with self.assertRaises(KeyError):
            result['type']

    def test_set_type_2(self):
        id = 'notfound'
        type = 'testing'
        self.d.setType(id, type)
        result = self.d.getId(id)
        self.assertEqual(result, None)

class FailTestCase(unittest.TestCase):
    def test_fail_config_0(self):
        # print('FILE NOT FOUND')
        with self.assertRaises(NameError):
            self.d = database.md.MongoDB('no_config')
            self.d._check_status()

    def test_fail_config_1(self):
        # print('NO CONFIG IN THE FILE')
        with self.assertRaises(NameError):
            self.d = database.md.MongoDB('test/test_config.ini')
            self.d._check_status()

if __name__ == '__main__':
    unittest.main()
