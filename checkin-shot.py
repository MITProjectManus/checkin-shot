#!/usr/local/bin/python3

import sys, os
import logging
import requests
import base64

from smtplib import SMTP_SSL as SMTP
from env import makerspaces, site_shot, email, output

def email_notify(msg):
	conn = SMTP(email['server'])
	conn.login(email['user'], email['pass'])
	conn.sendmail(email['sender'], email['recipients'], 'Subject: MAKE-IT-SO Error Generating Checkin Screenshot\n\n' + msg)
	conn.quit()

if(email['notify']):
	email_notify("All the stories are true!\n")