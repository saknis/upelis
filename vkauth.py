#!/usr/bin/env python
#
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
#from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import datastore_types
from google.appengine.api import images
from vkset import VKSettings
vkset1 = ""
vkset2 = ""
vkset3 = ""
vkset4 = ""
try:
    codelist = db.GqlQuery("SELECT * FROM VKSettings WHERE codename = :1", "vksettings")
    for code in codelist:
        vkset1 = code.vkset1
        vkset2 = code.vkset2
        vkset3 = code.vkset3
        vkset4 = code.vkset4
except:
    klaida=True
VK_ID = str(vkset1)
VK_APP_ID = str(vkset2).rstrip().lstrip()
VK_APP_SECRET = str(vkset3).rstrip().lstrip()
VK_URL = str(vkset4)


class VKUser(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)
    nickname = db.StringProperty()
    email = db.StringProperty(required=True)
    photomin = db.BlobProperty(required=True)



class BaseHandler(webapp.RequestHandler):
    @property
    def current_user(self):
        """Returns the logged in LINKEDIN user, or None if unconnected."""
        if not hasattr(self, "_current_user"):
            self._current_user = None
            user_id = parse_cookie(self.request.cookies.get("vk_user"))
            if user_id:
                self._current_user = VKUser.get_by_key_name(user_id)
        return self._current_user


class HomeHandler(BaseHandler):
    def get(self):
#        path = os.path.join(os.path.dirname(__file__), "oauth.html")
#        args = dict(current_user=self.current_user)
        current_user=self.current_user
        if current_user:
            aaa = """      <p><a href=\"%s\"><img src=\"/vkphoto/%s\" border=\"0\"></a></p>
            <p>You are logged in as %s</p>
            <p><a href=\"/vkauth/logout\">Log out</a></p>""" % (current_user.profile_url,current_user.id,current_user.name)
        else:
            aaa = """<p>You are not yet logged into this site</p>
            <p><a href=\"/vkauth/login\">Log in with VKONTAKTE</a></p>"""
        self.response.out.write(aaa)
#        self.response.out.write(template.render(path, args))
    def post(self):
        path = os.path.join(os.path.dirname(__file__), "vkoauth.html")
        args = dict(vk_current_user=self.current_user)
        self.response.out.write(template.render(path, args))


class LoginHandler(BaseHandler):
    def get(self):
        response=''
        profile=''
        s = StringIO.StringIO()
        verification_code = self.request.get("code")
        url = self.request.get("continue")
        if self.request.get("continue"):
#        	args = dict(client_id=VK_APP_ID, redirect_uri=self.request.path_url+("?continue=%s" % (urllib.quote(self.request.get("continue")))))
        	rurl = self.request.path_url+"?"+urllib.urlencode({'continue':url})
#r_fullprofile r_emailaddress rw_nus
        	args = dict(response_type='code',client_id=VK_APP_ID, redirect_uri=rurl, scope='friends,photos,email',v='5.1')
        else:
        	rurl = self.request.path_url
        	args = dict(response_type='code',client_id=VK_APP_ID, redirect_uri=rurl, scope='friends,photos,email',v='5.1')
        if self.request.get("code"):
        	args2 = dict(grant_type="authorization_code",client_id=VK_APP_ID, client_secret = VK_APP_SECRET,code = self.request.get("code"), redirect_uri=rurl)
        	try:
        	    hout=urllib.urlopen(
        	        "https://oauth.vk.com/access_token?" +
        	        urllib.urlencode(args2))
        	    response = json.load(hout)
        	    access_token = response['access_token']
        	    aerr=False
        	except:
        	    lines = ''.join(traceback.format_exception(*sys.exc_info()))
        	    pprint.pprint(response, s)
        	    pprint.pprint(lines, s)
        	    aerr=True
        	if not aerr and "email" in response and "user_id" in response:
#        	    variable = json.load(urllib.urlopen(
#        	    	"https://api.vk.com/method/getVariable?" +
#        	    	urllib.urlencode(dict(key='1280',access_token=access_token))))
        	    aaa=''
        	    vkuid='0'
        	    vkfirstname=''
        	    vklastname=''
        	    vknickname=''
        	    vkphoto="http://vk.com/images/camera_50.gif"
        	    userid=response['user_id']
        	    useremail=response['email']
        	    try:
        	        profile = json.load(urllib.urlopen(
        	            "https://api.vk.com/method/getProfiles?" +
        	            urllib.urlencode(dict(uid=userid,oauth2_access_token=access_token,fields='nickname,uid,first_name,last_name,photo,email'))))
        	    except:
        	        lines = ''.join(traceback.format_exception(*sys.exc_info()))
        	        pprint.pprint(profile, s)
        	        pprint.pprint(lines, s)
        	        aerr=True
        	    if "response" in profile:
        	        if "uid" in profile["response"][0]:
        	            vkuid=profile["response"][0]["uid"]
        	        if "first_name" in profile["response"][0]:
        	            vkfirstname=profile["response"][0]["first_name"]
        	        if "last_name" in profile["response"][0]:
        	            vklastname=profile["response"][0]["last_name"]
        	        if "nickname" in profile["response"][0]:
        	            vknickname=profile["response"][0]["nickname"]
        	        if "photo" in profile["response"][0]:
        	            vkphoto=profile["response"][0]["photo"]
#        	    for key in profile.keys(): 
#        	        pprint.pprint(profile[key], s)
#        	        json.dump(profile[key], s, sort_keys=True, indent=1)
#        	        pprint.pprint(s.getvalue(), ss)
#        	        aaa=aaa+u"<span style=\"font-size: 12pt\"><strong>%s.</strong>   </span><pre style=\"font-size: 8pt\">%s</pre>\n" % (key,s.getvalue())
#        	    self.response.out.write(aaa)
#        	    self.response.out.write("<br>\n%s %s %s %s %s<br>\n" % (vkuid, vkfirstname, vklastname, vknickname, vkphoto))
#        	    return
        	    vkprofileurl = "https://vk.com/id%s" % (vkuid)
        	    photourlcontblob = None
        	    photourlcont=urllib.urlopen(vkphoto).read()
        	    photourlcontmin = images.resize(photourlcont, width=50, height=50, output_encoding=images.PNG)
        	    photourlcontblob = db.Blob(photourlcontmin)
        	    try:
        	        user = VKUser(key_name=str(vkuid), id=str(vkuid),
        	        			name=("%s %s" % (vkfirstname,vklastname)), nickname = ("%s" % (vknickname)),
        	        			email=useremail, access_token=access_token,
        	        			profile_url=str(vkprofileurl),photomin=photourlcontblob)
        	        user.put()
        	        set_cookie(self.response, "vk_user", str(vkuid),expires=time.time() + 30 * 86400)
        	    except:
        	        lines = ''.join(traceback.format_exception(*sys.exc_info()))
        	        pprint.pprint(profile, s)
        	        pprint.pprint(lines, s)
        	        aerr=True
        	if aerr:
        		hout=s.getvalue()
        		self.response.out.write(hout)
        	elif self.request.get("continue"):
        		self.redirect(str(self.request.get("continue")))
        	else:
        		self.redirect("/vk")
        else:
            self.redirect(
                "https://oauth.vk.com/authorize?" +
                urllib.urlencode(args))


class LogoutHandler(BaseHandler):
    def get(self):
        set_cookie(self.response, "vk_user", "", expires=time.time() - 86400)
        if self.request.get("continue"):
        	self.redirect(str(self.request.get("continue")))
        else:
        	self.redirect("/vk")


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
    hash = hmac.new(VK_APP_SECRET, digestmod=hashlib.sha1)
    for part in parts: hash.update(part)
    return hash.hexdigest()


url_map = [(r"/vk", HomeHandler),(r"/vkauth/login", LoginHandler),(r"/vkauth/logout", LogoutHandler),]
app = webapp.WSGIApplication(url_map,debug=True)

