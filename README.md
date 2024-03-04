# Various Checkin Screen Experiments

## checkin-shot and checkin-trigger

These are a kludge to work around an issue loading Airtable screens on a digital signage player connected to the checkin displays in MIT makerspaces. These displays are supposed to show the list of currently checked in makers, along with their profile photos and credentials.

Metropolis and The Deep use donated BrightSign XT3 players which have a very basic ability to pull web pages into a presentation area. They struggle loading Airtable public view pages, which contain a lot of Javascript, asynchronously loaded content, and lots of data that is used to interact with the view (which is not possible from a digital sign). These pages take up to two minutes to load, so refreshing them frequently is not possible.

The above two Python programs implement a kludge-y workaround by taking site screenshots using the commerical site-shot API, and serving up static images to the BrightSign players. This kludge worked well in the beginning but failed several times on Airtable updates, which among other things added popups for GDPR compliance that could never be clicked away.

In this specific case we use the Site-Shot API, a reliable subscription service for taking screenshots of web pages. But Airtable is just not designed for this kind of hands-off use case of its public views.

## checkin_board

This is production solution to this problem, to move us away from the workaround. It is a simple Flask web application that loads an Airtable view via the Airtable API, and formats it for a checkin screen using a custom CSS file for color coding credentials and formatting other aspects of the screen.

It requires a certain format of the checkin view, and a makerspace-specific view be created in Airtable to match the spaces configured in `env.py`.

It can be run in a Python virtual environment, but does not have to be.

## Environment and Secrets

This program requires a local file, `env.py`, which sets several key variables used by the program. See the example below for reference:

```
# A dictionary of makerspaces to process. The keys need to match the "slug" field
# for each makerspace in Airtable. They also need to be file-system safe unique names
# They are used to create image filenames and to reference Airtable makerspace records.

# url: a URL to a public Airtable view to be site-shot into an image by the site-shot API
# view: the Airtable view ID for this space's checkin view
# name: the friendly name of this Makerspace used as the page title
# home: a list of makerspace slugs; credentials from any makerspace not listed
#       will be highlighted as transfer credentials
makerspaces = {
    'metropolis'  : {'url' : 'Public View URL', 'view' : 'View ID', 'name' : 'Metropolis' , 'home' : ['metropolis', 'thedeep']},
    'thedeep'     : {'url' : 'Public View URL', 'view' : 'View ID', 'name' : 'The Deep' , 'home' : ['metropolis', 'thedeep']},
    'beaverworks' : {'url' : 'Public View URL', 'view' : 'view ID', 'name' : 'BeaverWorks' , 'home' : ['beaverworks']}
}

# Airtable IDs for the checkin application
# base:  the Base ID of the production maker database
# table: the Table ID of the checkin sessions table
# category_sort_order: an ordered list specifying the display sort order for credentials
atcheckin = {
    'base'  : 'Base ID',
    'table' : 'Table ID',
    'category_sort_order' : ['Wood', 'Metal', 'Glass', 'Flame', 'FiberArts', 'Electronics', 'DigitalFab', 'Other', 'Training', 'Safety', 'External']
}

# Local configuration items. 'docroot' should be a full path
# underneath the web server's document root.
output = {
    'docroot' : './www/screenshots/'
}

# site-shot configuration includes a reload interval, which
# is the minimum reload interval. If triggers occur faster
# then reload is delayed until interval has passed.
site_shot = {
    'interval' : 60,
    'endpoint' : 'https://api.site-shot.com/',
    'userkey'  : 'Secret Key'
}

# SMTP email configuration for reporting critical failures
email = {
    'server' : 'SMTP Server',
    'notify' : True,
    'sender' : 'Sender Email Address',
    'recipients' : ['Recipient 1 Email Address', 'Recipient 2 Email Address'],
    'user' : 'username',
    'pass' : 'password' 
}

# regen: a local "secret" key that's required to be passed as a URL parameter to generate
#        a checkin screen; allows disabling of requests that consume API resources if
#        URLs become known
# airtable: Airtable personal access token with read access to checkin sessions table
keys = {
    'regen' : 'Regen Key',
    'airtable' : 'Personal Access Token'
}
```
