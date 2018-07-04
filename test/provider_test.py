import unittest
import provider
import datetime
import googlemaps

# SKENARIO 201
class TimeTestCase(unittest.TestCase):
    def setUp(self):
        self.p = provider.DataProvider()

    def test_time_process_0(self):
        # print('TIME FORMAT: 1 juni 2018 ')
        text = '1 Juni 2018'
        date = datetime.datetime(2018, 1, 1, 0, 0)

        expect = datetime.datetime(2018, 6, 1, 0, 0)
        result = self.p.time_process(text, date)
        self.assertEqual(expect, result)

    def test_time_process_1(self):
        # print('TIME FORMAT: June 21, 2018')
        text = 'June 21, 2018'
        date = datetime.datetime(2018, 2, 1, 0, 0)

        expect = datetime.datetime(2018, 6, 21, 0, 0)
        result = self.p.time_process(text, date)
        self.assertEqual(expect, result)

    def test_time_process_2(self):
        # print('TIME FORMAT: 21-06-2018')
        text = 'June 21, 2018'
        date = datetime.datetime(2018, 2, 1, 0, 0)

        expect = datetime.datetime(2018, 6, 21, 0, 0)
        result = self.p.time_process(text, date)
        self.assertEqual(expect, result)

# SKENARIO 203
class ExtractTextTestCase(unittest.TestCase):
    def setUp(self):
        self.p = provider.DataProvider()

    def test_extract_text_0(self):
        # print('LABEL FORMAT: B1 B2 I2 O O')
        text = ['lorem', 'ipsum', 'dolor', 'sit', '?']
        label = ['B-PLACE', 'B-TIME', 'I-TIME', 'O', 'O']

        expect = [
            {'label': 'PLACE', 'text': ['lorem']},
            {'label': 'TIME', 'text': ['ipsum', 'dolor']}
        ]
        result = self.p.extractText(label, text)
        self.assertEqual(expect, result)

    def test_extract_text_1(self):
        # print('LABEL FORMAT: B1 I1 O B2 B3 O O')
        text = ['lorem', 'ipsum', 'dolor', 'sit', 'amet', ',', 'consectetur']
        label = ['B-NAME', 'I-NAME', 'O', 'B-TIME', 'B-PLACE', 'O', 'O']

        expect = [
            {'label': 'NAME', 'text': ['lorem', 'ipsum']},
            {'label': 'TIME', 'text': ['sit']},
            {'label': 'PLACE', 'text': ['amet']}
        ]
        result = self.p.extractText(label, text)
        self.assertEqual(expect, result)

    def test_extract_text_2(self):
        # print('LABEL FORMAT: B1 B1 O B2 I3 O O')
        text = ['lorem', 'ipsum', 'dolor', 'sit', 'amet', ',', 'consectetur']
        label = ['B-INFO', 'B-INFO', 'O', 'B-TIME', 'I-PLACE', 'O', 'O']

        expect = [
            {'label': 'INFO', 'text': ['lorem']},
            {'label': 'INFO', 'text': ['ipsum']},
            {'label': 'TIME', 'text': ['sit']}
        ]
        result = self.p.extractText(label, text)
        self.assertEqual(expect, result)

    def test_extract_text_3(self):
        # print('LABEL FORMAT: B1 I1 O B1 I1 O O DUPLICATE TEST')
        text = ['lorem', 'ipsum', 'dolor', 'lorem', 'ipsum', 'sit', 'amet']
        label = ['B-INFO', 'I-INFO', 'O', 'B-INFO', 'I-INFO', 'O', 'O']

        expect = [
            {'label': 'INFO', 'text': ['lorem', 'ipsum']}
        ]
        result = self.p.extractText(label, text)
        self.assertEqual(expect, result)

# SKENARIO 202
class MapsTestCase(unittest.TestCase):
    def setUp(self):
        self.gmaps = googlemaps.Client(
            key='AIzaSyC9Jw099A_9uXyK8KFQPxR93-cg3ks5E40')
        self.p = provider.DataProvider()
        self.p.setMapClient(self.gmaps)

    def test_place_process(self):
        # print('PLACE: The Square Ballroom')
        text = 'The Square Ballroom'
        expect = [{'name':'The Square Ballroom', 'address':'ICBC Center L3, Jl. Basuki Rahmat 16-18, Kedungdoro, Tegalsari, Kota SBY, Jawa Timur 60261, Indonesia', 'location':{'lat':-7.2646499, 'lng':112.7407103}}]
        
        result = self.p.place_process(text)
        self.assertEqual(expect, result)

    def test_get_data(self):
        # print('DATA TEST: 999998633956265985')
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
        result = self.p.getData(id)
        self.assertEqual(expect['_id'], id)
        self.assertEqual(expect['label'], result['label'])
        self.assertEqual(expect['text'],  result['text'])
        self.assertEqual(expect['created_time'], result['created_time'])
        self.assertEqual(expect['source_url'],   result['source_url'])
        self.assertEqual(expect['image_url'],    result['image_url'])


if __name__ == '__main__':
    unittest.main()
