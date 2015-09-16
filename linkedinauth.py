#!/usr/bin/env python
#
# Copyright 2015 n.t.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.



import base64
import cgi
import Cookie
import email.utils
import hashlib
import hmac
import logging
import os.path
import time
import urllib
import wsgiref.handlers
import webapp2 as webapp
import uuid
import pprint, StringIO
import re
import sys
import traceback

import json
from google.appengine.ext import db
#from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import datastore_types
from google.appengine.api import images
from liset import LISettings
liset1 = ""
liset2 = ""
liset3 = ""
liset4 = ""
try:
    codelist = db.GqlQuery("SELECT * FROM LISettings WHERE codename = :1", "lisettings")
    for code in codelist:
        liset1 = code.liset1
        liset2 = code.liset2
        liset3 = code.liset3
        liset4 = code.liset4
except:
    klaida=True
LINKEDIN_ID = str(liset1)
LINKEDIN_APP_ID = str(liset2).rstrip().lstrip()
LINKEDIN_APP_SECRET = str(liset3).rstrip().lstrip()
LINKEDIN_URL = str(liset4)


class LIUser(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    nickname = db.StringProperty(required=True)
    email = db.StringProperty(required=True)
    photomin = db.BlobProperty(required=True)



class BaseHandler(webapp.RequestHandler):
    @property
    def current_user(self):
        """Returns the logged in LINKEDIN user, or None if unconnected."""
        if not hasattr(self, "_current_user"):
            self._current_user = None
            user_id = parse_cookie(self.request.cookies.get("li_user"))
            if user_id:
                self._current_user = LIUser.get_by_key_name(user_id)
        return self._current_user


class HomeHandler(BaseHandler):
    def get(self):
#        path = os.path.join(os.path.dirname(__file__), "oauth.html")
#        args = dict(current_user=self.current_user)
        current_user=self.current_user
        if current_user:
            aaa = """      <p><a href=\"%s\"><img src=\"/liphoto/%s\" border=\"0\"></a></p>
            <p>You are logged in as %s</p>
            <p><a href=\"/liauth/logout\">Log out</a></p>""" % (current_user.profile_url,current_user.id,current_user.name)
        else:
            aaa = """<p>You are not yet logged into this site</p>
            <p><a href=\"/liauth/login\">Log in with LINKEDIN</a></p>"""
        self.response.out.write(aaa)
#        self.response.out.write(template.render(path, args))
    def post(self):
        path = os.path.join(os.path.dirname(__file__), "lioauth.html")
        args = dict(li_current_user=self.current_user)
        self.response.out.write(template.render(path, args))


class LoginHandler(BaseHandler):
    def get(self):
        verification_code = self.request.get("code")
        url = self.request.get("continue")
        if self.request.get("continue"):
#        	args = dict(client_id=LINKEDIN_APP_ID, redirect_uri=self.request.path_url+("?continue=%s" % (urllib.quote(self.request.get("continue")))))
        	rurl = self.request.path_url+"?"+urllib.urlencode({'continue':url})
#r_fullprofile r_emailaddress rw_nus
        	args = dict(response_type='code',client_id=LINKEDIN_APP_ID, redirect_uri=rurl, scope='r_basicprofile r_emailaddress',state=uuid.uuid1())
        else:
        	rurl = self.request.path_url
        	args = dict(response_type='code',client_id=LINKEDIN_APP_ID, redirect_uri=rurl, scope='r_basicprofile r_emailaddress',state=uuid.uuid1())
        if self.request.get("code"):
        	args2 = dict(grant_type="authorization_code",client_id=LINKEDIN_APP_ID, client_secret = LINKEDIN_APP_SECRET,code = self.request.get("code"), redirect_uri=rurl)
        	hout=urllib.urlopen(
        	    "https://www.linkedin.com/uas/oauth2/accessToken?" +
        	    urllib.urlencode(args2))
        	response = json.load(hout)
        	aerr=False
        	try:
        	    access_token = response['access_token']
        	except:
        	    aerr=True
        	# Download the user profile and cache a local instance of the
        	# basic profile info
        	if not aerr:
        	    profile = json.load(urllib.urlopen(
        	    	"https://api.linkedin.com/v1/people/~:(id,first-name,last-name,public-profile-url,picture-urls::(50x50),email-address)?" +
        	    	urllib.urlencode(dict(oauth2_access_token=access_token,format="json"))))
#        	    liemail = urllib.urlopen(
#        	    	"https://api.linkedin.com/v1/people/~/email-address?" +
#        	    	urllib.urlencode(dict(oauth2_access_token=access_token,format="json"))).read()
#        	    liemail = liemail[1:-1]
        	    if not "emailAddress" in profile:
        	    	profile["emailAddress"] = "none"
#        	    	profile.update({'emailAddress':liemail})
        	    if not "publicProfileUrl" in profile:
        	    	profile["publicProfileUrl"] = "http://www.linkedin.com/profile/view?id=%s" % (profile["id"])
        	    photourlcontblob = None
        	    if "pictureUrls" in profile:
        	    	if "values" in profile["pictureUrls"]:
        	    	  photourl = str(profile["pictureUrls"]["values"][0])
        	    	  if re.match('^http', photourl):
        	    	    photourlcont=urllib.urlopen(photourl).read()
        	    	    photourlcontmin = images.resize(photourlcont, width=50, height=50, output_encoding=images.PNG)
        	    	    photourlcontblob = db.Blob(photourlcontmin)
#        	    aerr=True
        	    try:
        	        user = LIUser(key_name=str(profile["id"]), id=str(profile["id"]),
        	        			name=("%s %s" % (profile["firstName"],profile["lastName"])), nickname = ("%s %s" % (profile["firstName"],profile["lastName"])),
        	        			email=str(profile["emailAddress"]), access_token=access_token,
        	        			profile_url=str(profile["publicProfileUrl"]),photomin=photourlcontblob)
        	        user.put()
        	        set_cookie(self.response, "li_user", str(profile["id"]),expires=time.time() + 30 * 86400)
        	    except:
        	        lines = ''.join(traceback.format_exception(*sys.exc_info()))
        	        s = StringIO.StringIO()
        	        pprint.pprint(profile, s)
        	        pprint.pprint(liemail, s)
        	        pprint.pprint(lines, s)
        	        hout=s.getvalue()
        	        aerr=True
        	if aerr:
        		self.response.out.write(hout)
        	elif self.request.get("continue"):
        		self.redirect(str(self.request.get("continue")))
        	else:
        		self.redirect("/li")
        else:
            self.redirect(
                "https://www.linkedin.com/uas/oauth2/authorization?" +
                urllib.urlencode(args))


class LogoutHandler(BaseHandler):
    def get(self):
        set_cookie(self.response, "li_user", "", expires=time.time() - 86400)
        if self.request.get("continue"):
        	self.redirect(str(self.request.get("continue")))
        else:
        	self.redirect("/li")


def set_cookie(response, name, value, domain=None, path="/", expires=None):
    """Generates and signs a cookie for the give name/value"""
    timestamp = str(int(time.time()))
    value = base64.b64encode(value)
    signature = cookie_signature(value, timestamp)
    cookie = Cookie.BaseCookie()
    cookie[name] = "|".join([value, timestamp, signature])
    cookie[name]["path"] = path
    if domain: cookie[name]["domain"] = domain
    if expires:
        cookie[name]["expires"] = email.utils.formatdate(
            expires, localtime=False, usegmt=True)
#    response.headers._headers.append(("Set-Cookie", cookie.output()[12:]))
    response.headers['Set-Cookie'] = cookie.output()[12:]

def parse_cookie(value):
    """Parses and verifies a cookie value from set_cookie"""
    if not value: return None
    parts = value.split("|")
    if len(parts) != 3: return None
    if cookie_signature(parts[0], parts[1]) != parts[2]:
        logging.warning("Invalid cookie signature %r", value)
        return None
    timestamp = int(parts[1])
    if timestamp < time.time() - 30 * 86400:
        logging.warning("Expired cookie %r", value)
        return None
    try:
        return base64.b64decode(parts[0]).strip()
    except:
        return None


def cookie_signature(*parts):
    """Generates a cookie signature.

    We use the LINKEDIN app secret since it is different for every app (so
    people using this example don't accidentally all use the same secret).
    """
    hash = hmac.new(LINKEDIN_APP_SECRET, digestmod=hashlib.sha1)
    for part in parts: hash.update(part)
    return hash.hexdigest()


url_map = [(r"/li", HomeHandler),(r"/liauth/login", LoginHandler),(r"/liauth/logout", LogoutHandler),]
app = webapp.WSGIApplication(url_map,debug=True)

