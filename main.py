# -*- coding: utf-8 -*-
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
import datetime
import core
import logging
import sys
import urllib2, urllib
import uuid
import json
reload(sys)

sys.setdefaultencoding("utf-8")


try:
    import simplejson as json
except:
    import json

import os

from webapp2_extras import sessions
from google.appengine.ext import ndb

GAID = "UA-XXXXXX-X"

class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()


class Record(ndb.Model):
    number   = ndb.StringProperty(indexed=False)
    time     = ndb.StringProperty(indexed=False)
    to       = ndb.StringProperty(indexed=False)
    dir      = ndb.StringProperty(indexed=False)
    delay    = ndb.IntegerProperty(indexed=False)
    type     = ndb.StringProperty(indexed=False)
    station  = ndb.StringProperty(indexed=False)


class CollectHandler(BaseHandler):
    def get(self):

        stations   = self.request.get('station','1008')
        fetchDate = datetime.datetime.now()

	idxs = []

        client_id = uuid.uuid4()

        for station in stations.split(","):
            msg = core.crawl(fetchDate, station.strip())
            records = core.parser(fetchDate, msg)
        
            for record in records:

                if record['delay'] == 0:
                    continue

		if (record['index']+"_"+station) in idxs:
		    continue
		
		idxs.append(record['index']+"_"+station)

                key = ndb.Key("Record", record['index']+"_"+station)

                pushupRc = Record(key=key)
                pushupRc.populate(number=record["number"],
                                  time = record["time"],
                                  to   = record["to"],
                                  delay= record["delay"],
                                  type = record["type"],
                                  dir  = record["dir"],
                                  station= station
                                    )

                pushupRc.put()
	
            	logging.info(json.dumps(record) + " ST:"+ station)
    		form = {
	    		"v":"1",
	    		"tid": GAID,
            		"cid":client_id,
	    		"t" :"event",
	    		"ec":"North",
	    		"ea":"Delay",
	    		"el":record["type"],
	    		"ev":record["time"].split(":")[0],
	    		"cd1":station,
            		"cd2":record["number"], #train number
            		"cd3":record["dir"],
            		"cd4":record["to"],
	    		"cm1":int(record["delay"])
    		}
	
     
    		payload = urllib.urlencode(form)

		method = "http://www.google-analytics.com/collect"

		req = urllib2.Request(method, payload)
    		msg = (urllib2.urlopen(req)).read()

            logging.info(station + ":" + str(len(records)))


        
        return
class ExploreHandler(BaseHandler):
    def get(self):
        return

class GAHandler(BaseHandler):
    def get(self):
	
        client_id = uuid.uuid4()
    	form = {
	    "v":"1",
	    "tid": GAID,
            "cid":client_id,
	    "t":"event",
	    "ec":"TestNorth",
	    "ea":"Testdelay",
	    "el":"TrainType",
	    "cd1":"TestStation",
            "cd2":"TestTrain",
            "cd3":"TestDir",
	    "cm1":10
    	}
	
     
    	payload = urllib.urlencode(form)

	method = "http://www.google-analytics.com/collect"

	req = urllib2.Request(method, payload)
    	msg = (urllib2.urlopen(req)).read()

	self.response.write(client_id)
	return 


config = {}
config['webapp2_extras.sessions'] = {
        'secret_key': 'my-super-secret-key',
}

app = webapp2.WSGIApplication([
    ('/collect', CollectHandler),
    ('/ga', GAHandler)
   
], debug=True, config=config)
