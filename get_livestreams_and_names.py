import os
import csv
import re
import json
import StringIO
import codecs
import requests
import urllib

def get_cached_page(url):
    name = os.path.join(
        os.path.dirname(__file__),
        "cache", 
        url.split("://")[1].replace("/", "---")
    )
    if not os.path.exists(name):
        content = requests.get(url).content
        try:
            os.makedirs(os.path.dirname(name))
        except OSError:
            pass
        with codecs.open(name, 'w', 'utf-8') as fh:
            fh.write(content)
    with codecs.open(name, 'r', 'utf-8') as fh:
        content = fh.read()
    return content

reader = csv.reader(open("Hurricane Sandy livestreams - Sheet1.csv"))
sources = []
items = iter(reader)
items.next()
for url,locname,livethumb,notes in items:
    source = {
            'location': locname,
            'url': url,
            'livethumb': livethumb,
    }
    if "ustream" in url:
        source['provider'] = "ustream"
    elif "livestream" in url:
        source['provider'] = "livestream"
        source['id'] = re.search("livestream.com/([^/]+)/", url).group(1)
    elif "justin" in url:
        source['provider'] = "justintv"
        source['id'] = re.search("justin.tv/([^/#]+)(/|$|#)", url).group(1)
    elif "earthcam" in url:
        source['provider'] = "earthcam"
    else:
        assert False, "Unknown provider %s" % url

    latlng = json.loads(get_cached_page(
        "https://maps.googleapis.com/maps/api/geocode/json?sensor=false&address=%s" % urllib.quote_plus(locname.encode('utf8'))
    ))
    assert latlng['status'] != 'ZERO_RESULTS', "Geocode not found for %s" % locname
    source['point'] = latlng['results'][0]['geometry']['location']
    sources.append(source)

print "var data = %s" % json.dumps({'sources': sources})
