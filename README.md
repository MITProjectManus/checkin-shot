# Various Checkin Screen Experiments

## checkin_board

This is production solution to this problem, to move us away from the workaround. It is a simple Flask web application that loads an Airtable view via the Airtable API, and formats it for a checkin screen using a custom CSS file for color coding credentials and formatting other aspects of the screen.

It requires a certain format of the checkin view, and a makerspace-specific view be created in Airtable to match the spaces configured in `env.py`.

It can be run in a Python virtual environment, but does not have to be.

> Note that you WILL need to modify the Python program `checkin_board/__init__.py` before you run it in a new environment. It includes several MIT specific settings and presumes a lot of Airtable field structure in the code. However, it's a short 180 lines of code so should be easy to read and modify.

## checkin-shot and checkin-trigger

These are a kludge to work around an issue loading Airtable screens on a digital signage player connected to the checkin displays in MIT makerspaces. These displays are supposed to show the list of currently checked in makers, along with their profile photos and credentials.

Metropolis and The Deep use donated BrightSign XT3 players which have a very basic ability to pull web pages into a presentation area. They struggle loading Airtable public view pages, which contain a lot of Javascript, asynchronously loaded content, and lots of data that is used to interact with the view (which is not possible from a digital sign). These pages take up to two minutes to load, so refreshing them frequently is not possible.

The above two Python programs implement a kludge-y workaround by taking site screenshots using the commerical site-shot API, and serving up static images to the BrightSign players. This kludge worked well in the beginning but failed several times on Airtable updates, which among other things added popups for GDPR compliance that could never be clicked away.

In this specific case we use the Site-Shot API, a reliable subscription service for taking screenshots of web pages. But Airtable is just not designed for this kind of hands-off use case of its public views.

## Environment and Secrets

This program requires a local file, `env.py`, which sets several key variables used by the program. See the example below for reference:

```
# A dictionary of makerspaces to process. The keys need to be
# file-system safe unique names for each makerspace as they'll
# be used to create image directories by the screen shot program.
# The checkin_board code replaces the old screenshot code with a
# simple web app that displays current checkins for each
# makerspace. It needs the ID of the Airtable View, the name to
# display as the web page title, and the list of "home" makerspaces
# for which credentials will be shown.
#
makerspaces = {
    'zauberstube' : {'url' : 'URL to Public Airtable View', 'view' : 'viw0UUXVnxNPNvnwg', 'name' : 'Die Zauberstube', 'home' : ['zauberstube']}
}

idle_messages = [
    "No one is checked in right now. Hmmm... If no one is checked in right now, then who is reading this message???",
    "If a checkin screen falls in a makerspace and no one is checked in to hear it, does it make a sound?",
    "Is it me or does it seem really empty in here? Echo. Eeeeechooooo!",
    "(make-list 0 'makers) => nil",
    "Isn't the loneliest number really 0, not 1? It sure seems that way if your job is counting makers...",
    "Are you in here and not checked in? It's okay. I won't tell.",
]

# Airtable IDs for the checkin application
# base = the production Maker database, "Making at MIT" in the MIT environment
# table = the table holding checkin sessions, "Checkin Sessions" in the MIT environment
# View IDs for each makerspace's active checkins view are found in the makerspaces dict.
atcheckin = {
    'base'  : 'baseID',
    'table' : 'tableID',
    'category_sort_order' : ['Wood', 'Metal', 'Glass', 'Flame', 'FiberArts', 'Electronics', 'DigitalFab', 'Other', 'Training', 'Safety', 'External']
}

# Local configuration items. 'docroot' should be a full path
# underneath the web server's document root. For example, our
# web server document root for nginx running on macos installed
# via homebrew is /usr/local/var/www and we want to create a
# directory of images for each makerspace under
# /usr/local/var/www/checkin

output = {
    'docroot' : 'Local Output Directory for Screenshots'
}

# site-shot configuration includes a reload interval, which
# is the minimum reload interval. If triggers occur faster
# then reload is delayed until interval has passed.
site_shot = {
    'interval' : 60,
    'endpoint' : 'https://api.site-shot.com/',
    'userkey'  : 'Secret Key'
}

# SMTP email configuration for reporting critical failures.
# MIT uses TLS user/pass authenticated connections for its
# SMTP server. You may need to replace settings and modify the
# email notification code to match your SMTP server requirements.
email = {
    'server' : 'SMTP Server',
    'notify' : True,
    'sender' : 'Sender Email Address',
    'recipients' : ['email addresses to send to'],
    'user' : 'username',
    'pass' : 'password' 
}

# Keys
keys = {
    'regen' : 'made up unique key to protect from mischief',
    'airtable' : 'Airtable Personal Access Token'
}```
