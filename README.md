# Checkin Screenshot

Screenshot a large and script-heavy checkin screen and save it as a static image file. This script is specifically designed to deal with an issue with Airtable views (one of which is our "Who is checked into this makerspace?" view) not loading reliably on BrightSign digital signage boxes, which have very low-resourced browser capabilities that fail to reliably load Airtable and other Javascript heavy dynamic pages.

They load images really well, though, so we take advantage of one of the many site screenshot APIs to generate frequent static snapshots of the checkin screens that can then be displayed as images on digital signage.

In this specific case we use the Site-Shot API, a reliable subscription service for taking screenshots of web pages.
