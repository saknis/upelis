#!/usr/bin/env python
#
# Copyright 2010 Facebook
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

"""A barebones AppEngine application that uses Facebook for login.

This application uses OAuth 2.0 directly rather than relying on Facebook's
JavaScript SDK for login. It also accesses the Facebook Graph API directly
rather than using the Python SDK. It is designed to illustrate how easy
it is to use the Facebook Platform without any third party code.

See the "appengine" directory for an example using the JavaScript SDK.
Using JavaScript is recommended if it is feasible for your application,
as it handles some complex authentication states that can only be detected
in client-side code.
"""
""" modified Nerijus Terebas 2015.01.30"""

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

import json
from google.appengine.ext import db
#from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import datastore_types
from fbset import FBSettings
from facebook import GraphAPI
import pprint, StringIO
fbset1 = ""
fbset2 = ""
fbset3 = ""
fbset4 = ""
try:
    codelist = db.GqlQuery("SELECT * FROM FBSettings WHERE codename = :1", "fbsettings")
    for code in codelist:
        fbset1 = code.fbset1
        fbset2 = code.fbset2
        fbset3 = code.fbset3
        fbset4 = code.fbset4
except:
    klaida=True
FACEBOOK_ID = str(fbset1)
FACEBOOK_APP_ID = str(fbset2).rstrip().lstrip()
FACEBOOK_APP_SECRET = str(fbset3).rstrip().lstrip()
FACEBOOK_URL = str(fbset4)


class FBUser(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty()
    access_token2 = db.StringProperty(required=True)
    nickname = db.StringProperty()
    email = db.StringProperty(required=True)
    login = db.BooleanProperty()
    info = db.TextProperty() 
    perm = db.TextProperty() 


class BaseHandler(webapp.RequestHandler):
    @property
    def current_user(self):
        """Returns the logged in Facebook user, or None if unconnected."""
        if not hasattr(self, "_current_user"):
            self._current_user = None
            user_id = parse_cookie(self.request.cookies.get("fb_user"))
            if user_id:
                self._current_user = FBUser.get_by_key_name(user_id)
                if not self._current_user or not hasattr(self._current_user, "login") or not self._current_user.login:
                    self._current_user=None
        return self._current_user


class HomeHandler(BaseHandler):
    def get(self):
#        path = os.path.join(os.path.dirname(__file__), "oauth.html")
#        args = dict(current_user=self.current_user)
        current_user=self.current_user
        if current_user:
            aaa = """      <p><a href=\"%s\"><img src=\"http://graph.facebook.com/%s/picture\"/></a></p>
            <p>You are logged in as %s</p>
            <p><a href=\"/auth/logout\">Log out</a></p>""" % (current_user.profile_url,current_user.id,current_user.name)
        else:
            aaa = """<p>You are not yet logged into this site</p>
            <p><a href=\"/auth/login\">Log in with Facebook</a></p>"""
        self.response.out.write(aaa)
#        self.response.out.write(template.render(path, args))
    def post(self):
        path = os.path.join(os.path.dirname(__file__), "oauth.html")
        args = dict(current_user=self.current_user)
        self.response.out.write(template.render(path, args))


class LoginHandler(BaseHandler):
    def get(self):
        profile = {'id': 0}
        perm_mp=False	
        perm_pa=False	
        permtext=""	
        verification_code = self.request.get("code")
        url = self.request.get("continue")
        if self.request.get("continue"):
#        	args = dict(client_id=FACEBOOK_APP_ID, redirect_uri=self.request.path_url+("?continue=%s" % (urllib.quote(self.request.get("continue")))))
        	args = dict(client_id=FACEBOOK_APP_ID, redirect_uri=self.request.path_url+"?"+urllib.urlencode({'continue':url}), scope='email,manage_pages,publish_actions')
        else:
        	args = dict(client_id=FACEBOOK_APP_ID, redirect_uri=self.request.path_url)
        if self.request.get("code"):
            args["client_secret"] = FACEBOOK_APP_SECRET
            args["code"] = self.request.get("code")
            hout=urllib.urlopen(
                "https://graph.facebook.com/oauth/access_token?" +
                urllib.urlencode(args)).read()
            response = cgi.parse_qs(hout)
            aerr=False
            try:
                access_token = response["access_token"][-1]
            except:
                aerr=True
            # Download the user profile and cache a local instance of the
            # basic profile info
            if not aerr:
                permissions_str=""
                info_str=""
                profile = json.load(urllib.urlopen(
                	"https://graph.facebook.com/me?" +
                	urllib.urlencode(dict(access_token=access_token))))
                if not "email" in profile:
                	profile["email"] = 'none'
                if not profile["id"]==0:
                    try:
                        graph = GraphAPI(access_token)
                        permissions = graph.request("/v2.1/me/permissions")
                        for item in permissions["data"]:
                            if item["permission"]=="manage_pages" and item["status"] == "granted":
                                perm_mp=True	
                            if item["permission"]=="publish_actions" and item["status"] == "granted":
                                perm_pa=True	
                        if not perm_mp:
                            permtext = "manage_pages"
                        if not perm_pa:
                            permtext = permtext + " publish_actions"
#                        s = StringIO.StringIO()
#                        pprint.pprint(permissions["data"], s)
#                        permissions_str=s.getvalue()
                        permissions_str=permissions["data"]
                        if perm_mp and perm_pa:
                            if True:
                                mess = graph.request("/me/accounts")
#                                s1 = StringIO.StringIO()
#                                pprint.pprint(mess, s1)
#                                info_str=s1.getvalue()
                                info_str=mess["data"]
                                aaa=""			
                    except:
                        aaa=""

#import ast
#my_entity_k = db.Key.from_path('MyEntity', your_key_here)
#my_entity = db.get(my_entity_k)
#payload = ast.literal_eval(my_entity.dictionary_string)

                profusername=""
                if "username" in profile:
                	profusername=profile["username"]
                user = FBUser(key_name=str(profile["id"]), id=str(profile["id"]),
                			name=profile["name"], nickname=profusername,
                			email=profile["email"], access_token=access_token, access_token2=access_token,
                			profile_url=profile["link"],login=True,info=str(info_str),perm=str(permissions_str))
                user.put()
                set_cookie(self.response, "fb_user", str(profile["id"]),
                			expires=time.time() + 30 * 86400)
            if aerr:
            	self.response.out.write(hout)
            elif self.request.get("continue"):
            	self.redirect(str(self.request.get("continue")))
            else:
            	self.redirect("/fb")
        else:
            self.redirect(
                "https://graph.facebook.com/oauth/authorize?" +
                urllib.urlencode(args))


class LogoutHandler(BaseHandler):
    def get(self):
        set_cookie(self.response, "fb_user", "", expires=time.time() - 86400)
        user_id = parse_cookie(self.request.cookies.get("fb_user"))
        if user_id:
            fbdb = FBUser.get_by_key_name(user_id)
            fbdb.access_token=None
            fbdb.login=False
            fbdb.put()
        if self.request.get("continue"):
        	self.redirect(str(self.request.get("continue")))
        else:
        	self.redirect("/fb")


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

    We use the Facebook app secret since it is different for every app (so
    people using this example don't accidentally all use the same secret).
    """
    hash = hmac.new(FACEBOOK_APP_SECRET, digestmod=hashlib.sha1)
    for part in parts: hash.update(part)
    return hash.hexdigest()


url_map = [(r"/fb", HomeHandler),(r"/auth/login", LoginHandler),(r"/auth/logout", LogoutHandler),]
app = webapp.WSGIApplication(url_map,debug=True)

