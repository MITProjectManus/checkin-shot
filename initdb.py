import sqlite3
import time

# This program creates a minimal SQLite3 database file to hold basic server and
# Airtable API usage state as well as recent query results that need to be
# accessible across threads.
#
# It checks whether the DB exists, and if not, creates it and initializes the tables.
#
# For now, we only have one table which is "active_checkins". It contains all the
# fields we need from the Active Checkins view to create the checkin screen.
#
# In addition, each row has a "last_returned" timestamp to allow us to detect when
# the data was last fetched from the Airtable API so we know when to re-fetch it.
#
# Each row also has a "last_called" timestamp and a "return value" which is used to
# check whether there was a more recent fetch from the Airtable API that failed.
# For normal operation, the "last_called" timestamp and the "last_returned" 
# timestamp will be the same, and the "return value" will be 200, indicating success.
# 
# We store these extra fields for each row, even though the entire table is refreshed
# at the same time. In the future, we may partially refresh the table based on
# makerspace. (Also, I don't want to juggle two tables for now)

connection = sqlite3.connect('mystate.db')
cursor = connection.cursor()

# Create table to store API call state
cursor.execute('''
CREATE TABLE properties (
    last_called INTEGER,     -- Unix timestamp of most recent API call
    last_returned INTEGER    -- Unix timestamp of most recent successful return
)''')

# Initialize with current time
cursor.execute('INSERT INTO properties (last_called, last_returned) VALUES (?, ?)', 
              (int(time.time()), int(time.time())))

connection.commit()
connection.close()
