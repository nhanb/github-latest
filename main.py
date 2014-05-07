#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import json
import re
from google.appengine.api.urlfetch import fetch

API_LINK = 'https://api.github.com/repos/%s/%s/tags'

def latest_tag(tagnames):

    def dissemble(tag):
        match = re.match(r'^v?([0-9]+)\.([0-9]+)\.([0-9]+)-?([a-z0-9\.]*)$',
                         tag, flags=re.IGNORECASE)
        if match is None:
            raise Exception('malformed sematic version')

        major = match.group(1)
        minor = match.group(2)
        patch = match.group(3)
        # If crap after patch version (-rc.1, -alpha, etc.) is empty then bump
        # it to something that is guaranteed to be "greater than" (>) any other
        # possible crap string
        crap = match.group(4) or 'zzzzzzzzzz'
        return (major, minor, patch, crap)

    def compare(one, two):
        one = dissemble(one)
        two = dissemble(two)
        length = len(one)
        for i in range(length):
            if one[i] > two[i]:
                return 1
            elif one[i] < two[i]:
                return -1
        return 0

    latest = tagnames.pop()
    for tag in tagnames:
        if compare(tag, latest) > 0:
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
            self.response.write(latest)

            # Redirect to download link
            destination = self.request.get('dest')
            if destination:
                self.redirect(str(destination % latest))

        except ValueError:
            self.response.write('invalid url')
        except Exception, ex:
            self.response.write(ex)

app = webapp2.WSGIApplication([
    ('/.*', MainHandler)
], debug=True)
