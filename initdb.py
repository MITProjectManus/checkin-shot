import sqlite3

# This program creates a minimal SQLite3 database
# file to hold basic server and Airtable API usage
# state that needs to be accessible across threads.

# In particular the DB is used to hold a "last
# called" timestamp (we try not to call the API
# more frequently than once every 10 seconds or
# so to avoid rate limit failures).
#
# It also holds a "last returned" value so threads
# can no if a previous call failed.
#
# Lastly, it holds a backoff number (in seconds)
# to allow threads to back off calls if needed.
# A failure or rate limit exceed results in AT
# locking calls for 30 seconds, so that's the 
# initial backoff.
#
# Lastly lastly the DB stores a text blob of the
# most recently generated checkin screen for 
# each makerspace, along with a timestamp. We
# serve the screen from the DB if the request
# frequency exceeds the minimum delay, or 
# if we are in backoff mode.

connection = sqlite3.connect('mystate.db')
