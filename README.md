# Checkin Screenshot

Screenshot a large and script-heavy checkin screen and save it as a static image file. This script is specifically designed to deal with an issue with Airtable views (one of which is our "Who is checked into this makerspace?" view) not loading reliably on BrightSign digital signage boxes, which have very low-resourced browser capabilities that fail to reliably load Airtable and other Javascript heavy dynamic pages.

They load images really well, though, so we take advantage of one of the many site screenshot APIs to generate frequent static snapshots of the checkin screens that can then be displayed as images on digital signage.

In this specific case we use the Site-Shot API, a reliable subscription service for taking screenshots of web pages.

## Environment and Secrets

This program requires a local file, `env.py`, which sets several key variables used by the program. See the example below for reference:

```
# A dictionary of makerspaces to process. The keys need to be
# file-system safe unique names for each makerspace as they'll
# be used to create image directories.
makerspaces = {
    'makerspace1' : {'url' : 'AIRTABLE_VIEW_URL_FOR_MAKERSPACE1'},
    'makerspace2' : {'url' : 'AIRTABLE_VIEW_URL_FOR_MAKERSPACE1'},
    'makerspace3' : {'url' : 'AIRTABLE_VIEW_URL_FOR_MAKERSPACE1'}
}

# Local configuration items. 'docroot' should be a full path
# underneath the web server's document root. For example, our
# web server document root for nginx running on macos installed
# via homebrew is /usr/local/var/www and we want to create a
# directory of images for each makerspace under
# /usr/local/var/www/checkin

output = {
    'docroot' : '/usr/local/var/www/screenshots'
}

# site-shot configuration includes a reload interval, which
# is the minimum reload interval. If triggers occur faster
# then reload is delayed until interval has passed.
site_shot = {
    'interval' : 3600,
    'endpoint' : 'https://api.site-shot.com/',
    'userkey'  : 'SITE_SHOT_PAID_API_KEY'
}

# SMTP email configuration for reporting critical failures
email = {
    'server' : 'SMTP_SERVER',
    'notify' : True,
    'sender' : 'SENDER_EMAIL',
    'recipients' : ['RECIPIENT_EMAIL'],
    'user' : 'AUTH_USER',
    'pass' : 'AUTH_PASS' 
}

# A reload key that is verified for triggers requesting a reload
keys = {
    'reload' : 'RELOAD_KEY'
}
```

## Resulting Files

The most recent checkin screenshot for each makerspace will be saved as `latest.png`. Continuing the example outlined in `env.py` above, for a web server found at `https://makerspaces.mit.edu` this would result in:

```
https://makerspaces.mit.edu/screenshots/makerspace1/latest.png
https://makerspaces.mit.edu/screenshots/makerspace2/latest.png
https://makerspaces.mit.edu/screenshots/makerspace3/latest.png
```

always serving up the most recent screenshot of the checkin view for each of the three makerspaces. 10 previous screenshots are kept as `makerspace1_0.png` through `makerspace1_9.png`.

# Notifications

If outgoing email is configured, anything other than a success result code from the API call will result in a notification being mailed out to the configured error address.

# Programs

## `checkin-shot.py`

This program is designed to be runvia a system call or cron. It generates a set of screenshots via the Site-Shot API and deposits them into docroot. It also rotates previous screenshot files.

## `checkin-trigger.py`

This program implements a simple Flask endpoint to listen for a properly keyed trigger to fetch a new set of screenshots.
