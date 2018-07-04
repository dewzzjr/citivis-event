from flask import Flask, redirect, url_for, session, flash, render_template, request, abort
from flask_oauth import OAuth
import googlemaps
import urllib
from google import GoogleFactory
from provider import DataProvider
from mongo import MongoProvider
import json
import re
import sys

# You must configure these 3 values from Google APIs console
# https://code.google.com/apis/console
json_data = open('client_secret.json').read()
client = json.loads(json_data)

GOOGLE_CLIENT_ID = client['web']['client_id']
GOOGLE_CLIENT_SECRET = client['web']['client_secret']
REDIRECT_URI = '/authorized' # one of the Redirect URIs from Google APIs console

SECRET_KEY = 'mysecretkeyisverysecret'
DEBUG = True
PER_PAGE = 10
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()
gmaps = googlemaps.Client(key='AIzaSyC9Jw099A_9uXyK8KFQPxR93-cg3ks5E40')
# provider = DataProvider(mapClient=gmaps)
db = MongoProvider('config.ini')
api = GoogleFactory()
google = oauth.remote_app(
	'google',
	base_url='https://www.google.com/accounts/',
	authorize_url=client['web']['auth_uri'],
	request_token_url=None,
	request_token_params = {
		'scope':
			'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/calendar',
		'response_type': 'code'
	},
	access_token_url=client['web']['token_uri'],
	access_token_method='POST',
	access_token_params={'grant_type': 'authorization_code'},
	consumer_key=GOOGLE_CLIENT_ID,
	consumer_secret=GOOGLE_CLIENT_SECRET
)


def makeLabel(index, name, address):
	text = render_template(
		'map-label.var', name=name, address=address, index=index
	)
	text = re.sub(' +', ' ', text.strip())
	return text

def makeTitle(full_text):
	text = [s.strip() for s in full_text.splitlines()]
	text = text[0].split("|")[0]
	return text

def getProfile():
	access_token = session.get('access_token')
	if access_token is None:
		return None

	access_token = access_token[0]
	req = api.make_request_info(access_token)

	try:
		res = urllib.request.urlopen(req)
	except urllib.error.HTTPError as e:
		if e.code == 401:
			# Unauthorized - bad token
			session.pop('access_token', None)
			abort(401)
		return None
	return json.loads(res.read())

def addEventToCalendar(data, title, date, location):
	access_token = session.get('access_token')
	if access_token is None:
		return redirect(url_for('signin', next=url_for('insert_calendar')))

	access_token = access_token[0]
	req = api.make_request_calendar(access_token, data, title, date, location=location)
	try:
		res = urllib.request.urlopen(req)
	except urllib.error.HTTPError as e:
		flash(json.dumps(e.read()), "error")
		if e.code == 401:
			# Unauthorized - bad token
			session.pop('access_token', None)
			abort(401)
		return None
	return json.loads(res.read())

@app.route('/api/places', methods = ['POST'])
def get_place():
	data = request.get_json()
	# print(data)
	result = db.searchEventsByLocation(
		{'name': data['name'], 'address': data['address'], 'location': data['location']}
	)
	print(result.count())
	# return json.dumps(list(result))
	return render_template('sidelist.html', datas=result)

@app.route('/featured', defaults={ 'page' : 1, 'limit' : PER_PAGE })
@app.route('/featured/page/<int:page>', defaults={ 'limit' : PER_PAGE })
@app.route('/featured/page/<int:page>/limit/<int:limit>')
def home(page, limit):
	pass

@app.route('/detail/<string:id>')
def detail(id=None):
	if id is None:
		return abort(404)

	data = db.getId(id)
	if data is None:
		return abort(404)

	profile = getProfile()
	if profile is not None:
		session['profile_name'] = profile['name']
		session['profile_picture'] = profile['picture']
		session['email'] = profile['email']
	else:
		session.pop('profile_name', None)
		session.pop('profile_picture', None)
		session.pop('email', None)
	
	locations = []
	labels = []
	name_address = []

	if 'place' in data['entities'].keys():
		for index, d in enumerate(data['entities']['place']):
			locations.append(d['location'])
			name_address.append(
				{'name': d['name'], 'address': d['address'], 'location': d['location']}
			)
			text = makeLabel(index, d['name'], d['address'])
			labels.append(text)

	return render_template('detail.html', data=data, locations=locations, labels=labels, name_address=name_address)

@app.route('/')
@app.route('/search/<string:query>')
def index(query=None):
	if session.get('url'):
		url = session.pop('url', None)
		return redirect(url)

	profile = getProfile()
	if profile is not None:
		session['profile_name'] = profile['name']
		session['profile_picture'] = profile['picture']
		session['email'] = profile['email']
	else:
		session.pop('profile_name', None)
		session.pop('profile_picture', None)
		session.pop('email', None)

	locations = []
	labels = []
	name_address = []

	if query is None:
		data = db.getAllPlace()
		for index, d in enumerate(data):
			locations.append(d['location'])
			name_address.append(
				{'name': d['name'], 'address': d['address'], 'location': d['location']}
			)
			text = makeLabel(index, d['name'], d['address'])
			labels.append(text)
	else:
		data = gmaps.places(query=query)
		for index, d in enumerate(data['results']):
			locations.append(d['geometry']['location'])
			name_address.append(
				{'name': d['name'], 'address': d['formatted_address'], 'location': d['geometry']['location']}
			)
			text = makeLabel(index, d['name'], d['formatted_address'])
			labels.append(text)
			
	# datas = db.getEntries(0, 6)
	
	# return json.dumps(name_address)
	return render_template('index.html', locations=locations, labels=labels, name_address=name_address) 

@app.route('/signin')
def signin():
	url = request.args.get('next', url_for('index'))
	access_token = session.get('access_token')
	if access_token is None:
		session['url'] = url
		return redirect(url_for('login'))
	return redirect(url)

@app.route('/home')
def profile():
	# start: authentication google
	access_token = session.get('access_token')
	if access_token is None:
		return redirect(url_for('signin', url=url_for('profile')))
	profile = getProfile()
	
	if profile is not None:
		name = profile['name']
		img = profile['picture']
		return name, img
	else:
		return redirect(url_for('signin'))

@app.route('/add_reminder/<string:id>')
def insert_calendar(id):
	url = request.args.get('next', url_for('index'))
	data = db.getId(id)
	if 'name' in data['entities'].keys():
		title = data['entities']['name'][0]
	else:
		title = makeTitle(data['full_text'])

	if 'place' in data['entities'].keys():
		location = data['entities']['place'][0]['name']
	else:
		location = None

	if 'time' in data['entities'].keys():
		for date in data['entities']['time']:
			success = addEventToCalendar(data, title, date, location)
			message = 'Event has been added! <a target="_blank" href="https://calendar.google.com/calendar/r/day/{0}/{1}/{2}"> Please check your Calendar </a>'.format(date.year, date.month, date.day)
			flash(message)
			if success is None:
				flash("Event fail to add (1)", "error")
				return redirect(url_for('index'))
	else:
		flash("Event fail to add (0)", "error")
		return redirect(url_for('index'))
	
	return redirect(url)

@app.route('/login')
def login():
	callback = url_for('authorized', _external=True)
	return google.authorize(callback=callback)

@app.route('/logout')
def logout():
	url = request.args.get('next', url_for('index'))
	session.pop('access_token', None)
	session.pop('profile_name', None)
	session.pop('profile_picture', None)
	session.pop('email', None)
	flash('You were successfully logged out')
	return redirect(url)

@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
	access_token = resp['access_token']
	session['access_token'] = access_token, ''
	flash('You were successfully logged in')
	if 'url' in session:
		return redirect(session['url'])
	return redirect(url_for('index'))

@google.tokengetter
def get_access_token():
	return session.get('access_token')

def main():
	app.run(port=5000)

if __name__ == '__main__':
	main()
