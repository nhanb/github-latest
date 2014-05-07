#!/usr/bin/env python
import webapp2
import json
import re
from google.appengine.api.urlfetch import fetch

API_LINK = 'https://api.github.com/repos/%s/%s/tags'

class Semver(object):

    def __init__(self, version):
        match = re.match(r'^v?([0-9]+)\.([0-9]+)\.([0-9]+)-?([a-z0-9\.]*)$',
                         version, flags=re.IGNORECASE)
        if match is None:
            raise Exception('malformed sematic version')

        self.major = match.group(1)
        self.minor = match.group(2)
        self.patch = match.group(3)
        self.crap = match.group(4)

    def __cmp__(self, other):
        for attr in ['major', 'minor', 'patch']:
            this = getattr(self, attr) or 'zzzzz'  # Make empty greate than
            that = getattr(other, attr) or 'zzzzz' # non-empty crap
            if this > that:
                return 1
            elif this < that:
                return -1
        return 0

    def toString(self, format_str):
        if not format_str:
            format_str='%maj.%min.%pat%crap'
        replaces = {
            '%maj': self.major,
            '%min': self.minor,
            '%pat': self.patch,
            '%crap': self.crap,
        }
        for before, after in replaces.iteritems():
            format_str = format_str.replace(before, after)
        return format_str


def latest_tag(tagnames):
    tagnames = [Semver(tag) for tag in tagnames]
    latest = tagnames.pop()
    for tag in tagnames:
        if tag > latest:
            latest = tag
    return latest


class MainHandler(webapp2.RequestHandler):
    def get(self):
        try:
            user, repo = self.request.path.split('/')[1:]
            gh_resp = fetch(API_LINK % (user, repo))

            if gh_resp.status_code != 200:
                self.response.write('github screwed it up')
                return

            taglist = json.loads(gh_resp.content)
            tagnames = [tag[u'name'] for tag in taglist]
            latest = latest_tag(tagnames)

            format_str = self.request.get('format')
            latest_str = latest.toString(format_str)
            self.response.write(latest_str)

            # Redirect to download link
            destination = self.request.get('dest')
            if destination:
                self.redirect(str(destination % latest_str))

        except ValueError:
            self.response.write('invalid url')
        except Exception, ex:
            self.response.write(ex)

app = webapp2.WSGIApplication([
    ('/.*', MainHandler)
], debug=True)
