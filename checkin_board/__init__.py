from flask import Flask, render_template, request, redirect
from pyairtable import Table
from smtplib import SMTP_SSL as SMTP
from datetime import datetime
import random
import sqlite3

# Local env.py file containing runtime data that is not tracked in repo
# keys = dict with AT PAT and regen key
# makerspaces = list of makerspaces with slug, view, and name info
# atcheckin = AT IDs for this instance, category_sort_order list
from env import keys, makerspaces, atcheckin, email, idle_messages

app = Flask(__name__)

# Note: request IP can be found in request.remote_addr; allow 10.x.x.x and 127.0.0.1

# We use this SQLite3 DB to store state that needs to be shared across threads
connection = sqlite3.connect('mystate.db')

# A very simple home page. This is returned as the default in case of any
# malformed calls as well, to avoid broken or unauthorized API calls
@app.route("/")
def home():
	return(render_template('end.html'))

# Variable endpoint for rendering a makerspace checkin screen
# The string after /checkins/ must match a configured key in 
# the makerspaces dictionary AND the valid regen key needs to
# be passed, otherwise the call is redirected to the static /
# page and no API calls are made.
@app.route("/checkins/<makerspace>")
def checkin_screen(makerspace):
	#
	# There's probably a more efficient way to handle the
	# passing of a reload value in seconds
	#
	http_reload = 0
	if(request.args.get('reload')):
		# "reload" query param must be an integer
		try:
			http_reload = int(request.args.get('reload'))
		except ValueError:
			http_reload = 0

		# Also, we don't allow refesh intervals less that 10s (API calls = $$)
		if(http_reload < 10 and http_reload != 0):
			http_reload = 10

	# We add a subtle datetime and IP address string to the page
	if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
		remote_addr = request.environ['REMOTE_ADDR']
	else:
		remote_addr = request.environ['HTTP_X_FORWARDED_FOR']
	
	timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + remote_addr

	# Now on to checking the regen "secret"
	if(request.args.get('regen') == keys['regen'] and 
		(remote_addr.startswith('127.') or 
			remote_addr.startswith('10.'))):
		if(makerspace in makerspaces.keys()):
			return(makerspace_checkins(makerspace_slug = makerspace, makerspace_name = makerspaces[makerspace]['name'], http_reload=http_reload, timestamp=timestamp))
		else:
			return(redirect("/", code=302))
	else:
		return(redirect("/", code=302))

# Endpoint for the legend / info guide
@app.route("/checkins/docs/guide")
def guide():
	# This endpoint serves up a color and symbol key
	# to help users make sense of the checkin screen
	# credential colors and other symbology
	return(render_template('guide.html'))


def makerspace_checkins(makerspace_slug, makerspace_name, http_reload=0, timestamp=""):
	# Not that this call to Table is becoming deprecated in the pyairtable library and
	# should transition to using the Api.table() call instead.
	airtable_checkins = Table(keys['airtable'], atcheckin['base'], atcheckin['table'])

	try:
		checkins_list = airtable_checkins.all(view = makerspaces[makerspace_slug]['view'])
	except Exception as error_message:
		email_notify(repr(error_message))
		return(render_template('error.html', error = repr(error_message)))

	checkins = []
	if(len(checkins_list)):
		for line in checkins_list:
			this_checkin = {'Profile Photo':'', 'Display Name':'', 'Kerberos Name':'','Mentor':False, 'On Duty':False, 'Credentials':[]}

			if('Profile Photo' in line['fields'].keys()):
				this_checkin['Profile Photo'] = line['fields']['Profile Photo'][0]['url']

			if('Display Name' in line['fields'].keys()):
				this_checkin['Display Name'] = line['fields']['Display Name'][0]

			if('Kerberos Name' in line['fields'].keys()):
				if(len(line['fields']['Kerberos Name'])):
					this_checkin['Kerberos Name'] = line['fields']['Kerberos Name'][0]

			if('Roles' in line['fields'].keys()):
				if('Mentor' in line['fields']['Roles']):
					this_checkin['Mentor'] = True

			if('Survey Response' in line['fields'].keys()):
				if(line['fields']['Survey Response'] == 'on duty'):
					this_checkin['On Duty'] = True

			if('Compact-Full-Credential' in line['fields'].keys()):
				this_checkin['Credentials'] = clean_credentials(line['fields']['Compact-Full-Credential'], makerspaces[makerspace_slug]['home'])

			checkins.append(this_checkin)
	return(render_template('makerspace.html', checkins = checkins, slug = makerspace_slug, makerspace = makerspace_name, idle_message = random.choice(idle_messages), reload=http_reload, timestamp=timestamp))

@app.route("/checkins/error")
def checkins_error(error_message):
	email_notify(error_message)
	return(render_template('error.html', error = error_message))

def clean_credentials(credentials, home):
	# credentials = a list of the credentials as passed by Airtable, with fields '-' separated
	# slug = the slug for the current makerspace, e.g. 'metropolis'
	# home = a list of makerspaces considered "home" / not external, e.g. ['metropolis', 'thedeep']
	# 1. When adding to list, remove lower level of same credentials and remove duplicates; add Style value
    # 2. Credentials not earned in the "home" makerspaces are categorized as "External"
	# 3. Sort list by categories sort order as specified in env.py
	# Returns a sorted list with a short dict with Name, Category, Level, Style
	result = []
	for credential in credentials:
		clist = credential.split('-', 4)
		# Ignore any malformed credentials that are missing a level, category, or name
		if(len(clist) == 4):
			if(clist[3] in home):
				result = dedupe_and_append(result, {'Name':clist[2], 'Category':clist[1], 'Level':clist[0], 'Style':clist[1]+'-'+clist[0]})
			else:
				result = dedupe_and_append(result, {'Name':clist[2], 'Category':'External', 'Level':clist[0], 'Style':'External'})

	result = sorted(result, key = sortFn)
	return(result)

# Custom sort order for a list of credential dicts based on category_sort_order in env.py
def sortFn(credential):
	return(atcheckin['category_sort_order'].index(credential['Category']))

# Return a list of credential dicts with the new credential appended IF
# it does not already exist, and IF it is not superseded by a higher level
# credential of the same kind. Remove any lower-level credentials of the same kind.
def dedupe_and_append(credentials, credential):
	result = []
	addnew = True
	for item in credentials:
		if(item['Name'] == credential['Name'] and item['Level'] >= credential['Level']):
			# Duplicate Credential, do not append new
			addnew = False
			result.append(item)
		elif(item['Name'] == credential['Name'] and item['Level'] < credential['Level']):
			# Existing credential level is LOWER than new, do not append existing
			continue
		else:
			result.append(item)
	if(addnew):
		result.append(credential)
	return(result)



def email_notify(msg):
	conn = SMTP(email['server'])
	conn.login(email['user'], email['pass'])
	conn.sendmail(email['sender'], email['recipients'], 'Subject: Airtable API error when generating checkin screen\n\n' + msg)
	conn.quit()

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8000, debug=True)