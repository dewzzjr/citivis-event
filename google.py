from urllib import request, error, parse
import datetime
import json
# from database.md import MongoDB

class GoogleFactory(object):
    
    def __init__(self):
        self.BASE_URL = 'https://www.googleapis.com'
        # if isinstance(MongoDB):
        #     self.mongo = db

    def make_request_info(self, ACCESS_TOKEN):
        headers = {'Authorization': 'OAuth ' + ACCESS_TOKEN}
        url = self.BASE_URL + '/oauth2/v1/userinfo'
        req = request.Request(method='GET', url=url, headers=headers)
        # req = request.Request(self.BASE_URL + 'v1/userinfo', None, headers)
        return req

    def make_request_calendar(self, ACCESS_TOKEN, data, title, date, date_end=None, location=None):
        if not isinstance(date, datetime.datetime):
            return None

        if not isinstance(date_end, datetime.datetime):
            date_end = date
            
        headers = {
            'Authorization': 'OAuth ' + ACCESS_TOKEN,
            'Content-Type': 'application/json'
        }
        url = self.BASE_URL + '/calendar/v3/calendars/primary/events'
        body = {
            'summary': title,
            'htmlLink': data['source_url'],
            'description': data['full_text'],
            'start': {
                'date': date.strftime('%Y-%m-%d')
            },
            'end': {
                'date': date_end.strftime('%Y-%m-%d')
            },
            'attachments': [
                {
                    "fileUrl": data['image_url']
                }
            ]
        }
        if location is not None:
            body['location'] = location
        
        body = bytes(json.dumps(body), encoding="utf-8")
        print(body)
        print(url)
        req = request.Request(
            method='POST',
            url=url,
            headers=headers,
            data=body
        )
        return req
