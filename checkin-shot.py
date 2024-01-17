#!/usr/local/bin/python3

import sys, os, subprocess, pathlib, time
import logging
import requests
import base64
import argparse

from smtplib import SMTP_SSL as SMTP
from env import makerspaces, site_shot, email, output, keys

def email_notify(msg):
	conn = SMTP(email['server'])
	conn.login(email['user'], email['pass'])
	conn.sendmail(email['sender'], email['recipients'], 'Subject: MAKE-IT-SO Error Generating Checkin Screenshot\n\n' + msg)
	conn.quit()


def get_screenshot(params):
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain",
               "userkey": site_shot['userkey']}

    try:
        r = requests.post('https://api.site-shot.com/', headers=headers, data=params)

        if (r.status_code == requests.codes.ok):
            return r.json()
        elif (r.status_code == 404):
        	logging.error("Screenshot hasn't been generated. The error: " + r.json().error)
        	email_notify("Screenshot hasn't been generated. The error: " + r.json().error)
        elif (r.status_code == 401):
        	logging.error("Invalid authentication token")
        	email_notify("Screenshot hasn't been generated. Invalid authentication token.")
        elif (r.status_code == 403):
        	logging.error("Active subscription hasn't been found")
        	email_notify("Screenshot hasn't been generated. No active subscription found.")
    except requests.exceptions.RequestException as e:
    	logging.error("Screenshot generation has failed with error: " + str(e))
    	email_notify("Screenshot generation has failed with error: " + str(e))

def makerspace_checkin_screen(makerspace, args):
	# This function takes a makerspace name as an argument, and
	# then runs through the process to (maybe) generate a new
	# checkin screen screenshot for this makerspace.
	# 1. Is this makerspace on of the keys in the makerspaces dict?
	# 2. Is there a timestamp file for this makerspace? If not make one and return.
	# 3. Is there a request file for this makerspace with a timestamp AFTER the timestamp file? If not, return.
	# 4. Is the timestamp file older than (now - interval)? If not, return.
	# 5. Call get_screenshot for this makerspace, save the screenshot, and update the timestamp file.
	if makerspace not in makerspaces:
		return(404)
	timefile = output['docroot'] + makerspace + '.lst'
	if(not os.path.exists(timefile)):
		logging.warning("Timestamp file {} for {} does not exist. Creating but skipping screenshot.".format(timefile, makerspace))
		subprocess.run(["touch", timefile])
		return(412)
	now = time.time()
	timefile_mt = os.path.getmtime(timefile)
	requestfile = output['docroot'] + makerspace + '.req'
	# Check for the existence of a request file or the flag to ignore it
	if(not os.path.exists(requestfile) and not args['regular']):
		logging.debug("Request file {} for {} does not exist.".format(requestfile, makerspace))
		return(412)
		requestfile_mt = os.path.getmtime(requestfile)
		if(requestfile_mt < timefile_mt):
			logging.debug("Request file {} is older than last screenshot for {}.".format(requestfile, makerspace))
			return(412)
	if(now - timefile_mt < site_shot['interval']):
		logging.debug("Minimum time interval not yet reached to update screenshot for {}".format(makerspace))
		return(412)
	screenshot = get_screenshot(
		{'url': makerspaces[makerspace]['url'],
		'width': args['width'],
		'height': args['height'],
		'zoom': args['zoom'],
		'format': 'png',
		'response_type': 'json',
		'delay_time': site_shot['delay_time'],
		'timeout': site_shot['timeout']})
	if screenshot is None:
		logging.error("Screenshot generation failed.")
		return(500)
	base64_image = screenshot['image'].split(',', maxsplit=1)[1]
	image_file = open(output['docroot'] + makerspace + '.png', 'wb')
	image_file.write(base64.b64decode(base64_image))
	image_file.close()
	subprocess.run(['touch', timefile])
	return(200)

def main(args):
	logging.debug("Log Level: {}".format(args['loglevel']))
	logging.debug("Regular Intervals? {}.".format(args['regular']))
	logging.debug("Width: {}".format(args['width']))
	logging.debug("Height: {}".format(args['height']))
	logging.debug("Zoom: {}".format(args['zoom']))
	logging.debug("Configuration: {}".format(args['config']))

	# Using a passed url is currently unimplemented. The idea
	# is that it would be useful to do a quick on-demand screen
	# shot.
	# if(args['url']):
	#	logging.debug("One-time URL: {}".format(args['url']))

	lockfile = output['docroot'] + 'lockfile'
	if(not os.path.exists(lockfile)):
		subprocess.run(["touch", lockfile])
		makerspace_checkin_screen('metropolis', args)
		makerspace_checkin_screen('thedeep', args)
		# makerspace_checkin_screen('beaverworks', args)
		# makerspace_checkin_screen('shed', args)
		subprocess.run(["rm", lockfile])
	else:
		logging.warning("Lockfile exists. Another checkin-shot process may already be running.")
		email_notify("Lockfile exists while running checkin-shot. Attention may be needed.")

#	timefile = output['docroot'] + 'metropolis' + '.lst'
#	if(os.path.exists(timefile)):
#   	# Timestamp file for this makerspace exists, do the time check
#		now = time.time()
#		timefile_mt = os.path.getmtime(timefile)
#		if(now - timefile_mt > site_shot['interval']):
#			# The minimum required interval has passed and we can get another
#			# screen shot
#			screenshot = get_screenshot(
#				{'url': makerspaces['metropolis']['url'],
#				 'width': args['width'],
#				 'height': args['height'],
#				 'zoom' : args['zoom'],
#				 'format': 'png',
#				 'response_type': 'json',
#				 'delay_time': 1500,
#				 'timeout': 60000})
#
#			if screenshot is not None:
#				base64_image = screenshot['image'].split(',', maxsplit=1)[1]
#				image_file = open(output['docroot'] + 'metropolis' + '.png', 'wb')
#				image_file.write(base64.b64decode(base64_image))
#				image_file.close()
#				subprocess.run(['touch', timefile])
#		else:
#			logging.warning("{} seconds since last screenshot. Minimum time interval has not yet passed.".format(now - timefile_mt))
#	else:
#		logging.warning("Timestamp file {} does not exists. Creating but skipping screenshot.".format(timefile))
#		subprocess.run(['touch', timefile])

if __name__ == '__main__':
	# All arguments are optional. Defaults are either specified below or pulled from env.py
	parser = argparse.ArgumentParser()
	# parser.add_argument('url')
	parser.add_argument('-c', '--config', default='env.py', help='Alternate env.py configuration file')
	parser.add_argument('-r', '--regular', action='store_true', help='Ignore presence of a request file and run at regular intervals')
	parser.add_argument('-W', '--width',    type=int, default=1430, help='Width of the requested browser snapshot, default = 1430')
	parser.add_argument('-H', '--height',   type=int, default=1080, help='Height of the requested browser snapshot, default = 1080')
	parser.add_argument('-Z', '--zoom',     type=int, default=125, help='Virtual browser zoom level, default = 25')
	parser.add_argument('-l', '--loglevel', default='WARNING', help='Log level (DEBUG|INFO|WARNING|ERROR|CRITICAL)')
	parser.add_argument('-v', '--verbose',  action='store_true', help='Verbose mode forces log level to DEBUG')
	args = parser.parse_args()

	# Set log level
	loglevel = vars(args)['loglevel']
	if(vars(args)['verbose']):
		loglevel = 'DEBUG'
	numeric_log_level = getattr(logging, loglevel.upper(), None)
	if not isinstance(numeric_log_level, int):
		raise ValueError('Invalid log level: %s' % log_level)
	logging.basicConfig(level=numeric_log_level)
	logging.debug(vars(args))
	main(vars(args))