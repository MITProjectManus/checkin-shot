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

# Document root to place files into. This should be a full path
# underneath the web server's document root. For example, our
# web server document root for nginx running on macos installed
# via homebrew is /usr/local/var/www and we want to create a
# directory of images for each makerspace under
# /usr/local/var/www/checkin
checkin_document_root = '/usr/local/var/www/checkin'

# site-shot configuration
site_shot = {
    'interval' : 3600,
    'endpoint' : 'https://api.site-shot.com/',
    'userkey'  : 'SITE_SHOT_API_KEY'
}
```

## Resulting Files

The most recent checkin screenshot for each makerspace will be saved as `latest.png`. Continuing the example outlined in `env.py` above, for a web server found at `https://makerspaces.mit.edu` this would result in:

```
https://makerspaces.mit.edu/checkin/makerspace1/latest.png
https://makerspaces.mit.edu/checkin/makerspace2/latest.png
https://makerspaces.mit.edu/checkin/makerspace3/latest.png
```

always serving up the most recent screenshot of the checkin view for each of the three makerspaces. 10 previous screenshots are kept as `makerspace1_0.png` through `makerspace1_9.png`.

# Notifications

If outgoing email is configured, 
