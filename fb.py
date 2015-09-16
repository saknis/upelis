#!/usr/bin/env python
# -*- coding:utf8 -*-
#
# Copyright 2015 Nerijus Terebas.
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


__author__ = 'Nerijus Terebas'

import os
import cgi
import sys
import urllib
import json
#from pprint import pprint
import webapp2 as webapp
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import datastore
from google.appengine.api import datastore_types
import pprint, StringIO
import json
#import ast
from upelis_settings import *

cmsname2=CMSNAME
cmspath2=CMSPATH
cmstrans2=CMSTRANS
site1a=SITE1A
site1b=SITE1B
site2a=SITE2A
site2b=SITE2B
sitedown=SITEDOWN

def urlhost2():
	if os.environ['HTTPS']=="off":
		return str('http://'+os.environ['HTTP_HOST'])
	else:
		return str('https://'+os.environ['HTTP_HOST'])


from fbset import FBSettings
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
FACEBOOK_APP_ID = str(fbset2)
FACEBOOK_APP_SECRET = str(fbset3)
FACEBOOK_URL = str(fbset4)

from facebook import GraphAPI

# Set to true if we want to have our webapp print stack traces, etc
_DEBUG = True

class FriendsInfo(webapp.RequestHandler):

  def get(self):
    import facebookoauth
    from facebookoauth import FBUser
    import pprint, StringIO

    co2=100
    aaa=""
    pg=self.request.get('pg')
    if pg:
      pg = int(pg)
    else:
      pg=0
    hout = ""
    prid=self.request.get('id')
    args = dict(grant_type="client_credentials", client_id=FACEBOOK_APP_ID, client_secret=FACEBOOK_APP_SECRET)
    response = cgi.parse_qs(urllib.urlopen("https://graph.facebook.com/oauth/access_token?" +urllib.urlencode(args)).read())
    access_token = response["access_token"][-1]
    #print access_token
    errorjson = False
    profile = {'id': 0}
    try:
        graph = GraphAPI(access_token)
        profile = graph.get_object(prid)
    except Exception, e:
        errorjson = True
        errtext =  cgi.escape(str(sys.exc_info()[0])) + ' ' + cgi.escape(str(sys.exc_info()[1])) + ' ' + cgi.escape(str(sys.exc_info()[2]))
#            s = StringIO.StringIO()
#            pprint.pprint(permissions, s)
#            hout=s.getvalue()
    cover = None
    if 'cover' in profile:
        strdict=profile['cover']
        try:
            if 'source' in strdict:
                cover = strdict['source']
        except Exception, e:
            errorjson = True
            errtext =  cgi.escape(str(sys.exc_info()[0])) + ' ' + cgi.escape(str(sys.exc_info()[1])) + ' ' + cgi.escape(str(sys.exc_info()[2]))
            cover = None
    if not users.is_current_user_admin():
        if 'email' in profile:
            del profile['email']
        if 'phone' in profile:
            del profile['phone']
    for key in profile.keys():
		value = profile[key]
		if type(value) is list:		
			i = 0
			while i < len(value):
				value2=value[i]
				if type(value2) is dict:		
					for key3 in value2.keys(): 
						if str(key3)  == 'id':
							value2[key3+'_ntinfo'] = "<a href='/fbinfo?id=%s'>%s</a>" % (value2[key3],value2[key3])
				profile[key][i]=value2
				i += 1
		if type(value) is dict:		
			for key2 in value.keys(): 
				if str(key2)  == 'id':
					profile[key][key2+'_ntinfo'] = "<a href='/fbinfo?id=%s'>%s</a>" % (profile[key][key2],profile[key][key2])
			#print profile
    bbb=""
    aaa=""
    if errorjson:
        aaa=aaa+"%s" % (errtext)
    if cover:
        aaa=aaa+u"<img src=\"%s\"/><br />\n" % (cover)
    aaa=aaa+u"<a href=\"http://www.facebook.com/profile.php?id=%s\"><img src=\"http://graph.facebook.com/%s/picture?type=large\"/></a><br />\n" % (profile['id'],profile['id'])
    for key in profile.keys(): 
        s = StringIO.StringIO()
        ss = StringIO.StringIO()
        #pprint.pprint(profile[key], s)
        json.dump(profile[key], s, sort_keys=True, indent=1)
        #pprint.pprint(s.getvalue(), ss)
        aaa=aaa+u"<span style=\"font-size: 12pt\"><strong>%s.</strong>   </span><pre style=\"font-size: 8pt\">%s</pre>\n" % (key,s.getvalue())
    aaa=aaa+"<br>\n"
    aaa="<h1>FaceBook User <a href=\"http://www.facebook.com/profile.php?id=%s\">%s</a> info</h1><p>%s</p><p><a href=\"/fbputwall?cmd=delperm\">delete permision</a></p>" % (profile['id'],profile['id'],aaa)
    self.response.out.write("<html><body> %s </body></html>" % (aaa))

				
class FBPutWall(webapp.RequestHandler):

  def get(self):
    import facebookoauth
    from facebookoauth import FBUser
    import pprint, StringIO

#    prid=self.request.get('id')
#    prid="me"
#    args = dict(grant_type="client_credentials", client_id=FACEBOOK_APP_ID, client_secret=FACEBOOK_APP_SECRET)
#    response = cgi.parse_qs(urllib.urlopen("https://graph.facebook.com/oauth/access_token?" +urllib.urlencode(args)).read())
#    access_token = response["access_token"][-1]
    #print access_token
    hout = ""
    user_id = facebookoauth.parse_cookie(self.request.cookies.get("fb_user"))
    errorjson = False
    aaa="<h2>wall post</h2>error"
    profile = {'id': 0}
    perm_mp=False	
    perm_pa=False	
    permtext=""	
    cmd=self.request.get('cmd')
    oid=self.request.get('oid')
    if user_id:
      fb2_current_user = FBUser.get_by_key_name(user_id)
      if fb2_current_user and fb2_current_user.login:
        try:
            graph = GraphAPI(fb2_current_user.access_token)
            profile = graph.get_object("me")
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
            s = StringIO.StringIO()
#            pprint.pprint(permissions, s)
            message = "Zinute patalpinta per\n"+urlhost2()+"/fbputwall"        
            attachment = {}  
            attachment['name'] = "Nerijaus Terebo turinio valdymo sistemele \"Upelis\""  
            attachment['caption'] = site1b  
            attachment['link'] = 'http://'+site1b  
            attachment['picture'] = urlhost2()+'/static/images/upelis116.jpg'  
            attachment['description'] = 'Turinio valdymo sistemele \"Upelis\" - Python, AppEngine'  
            if cmd =="delperm":
#                    mess = graph.delete_object(oid)
#                    mess = graph.request(oid, post_args={"method": "delete"})
                post_args=dict(method = "delete", access_token = fb2_current_user.access_token)
                post_data = urllib.urlencode(post_args)
                file = urllib.urlopen("https://graph.facebook.com/me/permissions" , post_data)
                try:
                    response = json.loads(file.read())
                finally:
                    file.close()
                #pprint.pprint(response, s)
                json.dump(response, s, sort_keys=True, indent=1)
                hout=s.getvalue()
                aaa="<h2>permissions delete - ok </h2><pre>%s</pre>" % (hout)			
            elif not perm_mp or not perm_pa:
                aaa="<h2>wall post - error - registruodamiesi nepatvirtinot: %s  </h2><br><pre>%s</pre>" % (permtext,hout)			
            else:
                if cmd =="delete":
#                    mess = graph.delete_object(oid)
#                    mess = graph.request(oid, post_args={"method": "delete"})
                    post_args=dict(method = "delete", access_token = fb2_current_user.access_token)
                    post_data = urllib.urlencode(post_args)
                    file = urllib.urlopen("https://graph.facebook.com/" + oid , post_data)
                    try:
                        response = json.loads(file.read())
                    finally:
                        file.close()
                    #pprint.pprint(response, s)
                    json.dump(response, s, sort_keys=True, indent=1)
                    hout=s.getvalue()
                    aaa="<h2>wall post delete - ok </h2><pre>%s</pre>" % (hout)			
                elif cmd =="info":
                    mess = graph.request("/me/accounts")
                    json.dump(mess, s, sort_keys=True, indent=1)
                    #pprint.pprint(mess, s)
                    hout=s.getvalue()
                    aaa="<h2>accounts info</h2><p><pre>%s</pre></p>" % (hout)			
                elif cmd =="friends":
                    mess = graph.request("/v2.3/me/friends")
                    json.dump(mess, s, sort_keys=True, indent=1)
                    #pprint.pprint(mess, s)
                    hout=s.getvalue()
                    aaa="<h2>friends</h2><p><pre>%s</pre></p>" % (hout)			
                else:
                    mess = graph.put_wall_post(message, attachment=attachment)
                    json.dump(mess, s, sort_keys=True, indent=1)
                    #pprint.pprint(mess, s)
                    hout=s.getvalue()
                    aaa="<h2>wall post - ok </h2><p><a href=\"/fbputwall?cmd=delete&oid=%s\">delete</a></p><pre>%s</pre>" % (mess["id"],hout)			
        except Exception, e:
            errorjson = True
            errtext =  cgi.escape(str(sys.exc_info()[0])) + ' ' + cgi.escape(str(sys.exc_info()[1])) + ' ' + cgi.escape(str(sys.exc_info()[2]))
      else:
        aaa="<h2>wall post</h2>not loged - <a href=\"/auth/login?continue=%s\">login</a>" % (urllib.quote(self.request.uri))
    else:
      aaa="<h2>wall post</h2>not loged - <a href=\"/auth/login?continue=%s\">login</a>" % (urllib.quote(self.request.uri))
    bbb=""
    if errorjson:
        aaa=aaa+"%s" % (errtext)
    aaa="<h1>FaceBook User <a href=\"%s\">%s</a> info</h1><p>%s</p>" % (profile['link'],profile['id'],aaa)
    self.response.out.write("<html><body> %s </body></html>" % (aaa))



def putwall(req,message,attachment):
    import facebookoauth
    from facebookoauth import FBUser
    import pprint, StringIO

#    prid=self.request.get('id')
#    prid="me"
#    args = dict(grant_type="client_credentials", client_id=FACEBOOK_APP_ID, client_secret=FACEBOOK_APP_SECRET)
#    response = cgi.parse_qs(urllib.urlopen("https://graph.facebook.com/oauth/access_token?" +urllib.urlencode(args)).read())
#    access_token = response["access_token"][-1]
    #print access_token
    hout = ""
    user_id = facebookoauth.parse_cookie(req.request.cookies.get("fb_user"))
    errorjson = False
    aaa="<h2>wall post</h2>error"
    profile = {'id': 0}
    perm_mp=False	
    perm_pa=False	
    permtext=""	
    cmd=req.request.get('cmd')
    oid=req.request.get('oid')
    if user_id:
      fb2_current_user = FBUser.get_by_key_name(user_id)
      if fb2_current_user and fb2_current_user.login:
        try:
            graph = GraphAPI(fb2_current_user.access_token)
            profile = graph.get_object("me")
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
            s = StringIO.StringIO()
#            pprint.pprint(permissions, s)
#            message = "Zinute patalpinta per\nhttp://www.nerij.us/fbputwall"        
#            attachment = {}  
#            attachment['name'] = "Nerijaus Terebo turinio valdymo sistemele \"Upelis\""  
#            attachment['caption'] = 'www.upelis.org'  
#            attachment['link'] = 'http://www.upelis.org/'  
#            attachment['picture'] = 'http://www.nerij.us/static/images/upelis116.jpg'  
#            attachment['description'] = 'Turinio valdymo sistemele \"Upelis\" - Python, AppEngine'  
            if cmd =="delperm":
#                    mess = graph.delete_object(oid)
#                    mess = graph.request(oid, post_args={"method": "delete"})
                post_args=dict(method = "delete", access_token = fb2_current_user.access_token)
                post_data = urllib.urlencode(post_args)
                file = urllib.urlopen("https://graph.facebook.com/me/permissions" , post_data)
                try:
                    response = json.loads(file.read())
                finally:
                    file.close()
                json.dump(response, s, sort_keys=True, indent=1)
                #pprint.pprint(response, s)
                hout=s.getvalue()
                aaa="<h2>permissions delete - ok </h2><pre>%s</pre>" % (hout)			
            elif not perm_mp or not perm_pa:
                aaa="<h2>wall post - error - registruodamiesi nepatvirtinot: %s  </h2><br><pre>%s</pre>" % (permtext,hout)			
            else:
                if cmd =="delete":
#                    mess = graph.delete_object(oid)
#                    mess = graph.request(oid, post_args={"method": "delete"})
                    post_args=dict(method = "delete", access_token = fb2_current_user.access_token)
                    post_data = urllib.urlencode(post_args)
                    file = urllib.urlopen("https://graph.facebook.com/" + oid , post_data)
                    try:
                        response = json.loads(file.read())
                    finally:
                        file.close()
                    #pprint.pprint(response, s)
                    json.dump(response, s, sort_keys=True, indent=1)
                    hout=s.getvalue()
                    aaa="<h2>wall post delete - ok </h2><pre>%s</pre>" % (hout)			
                elif cmd =="info":
                    mess = graph.request("/me/accounts")
                    #pprint.pprint(mess, s)
                    json.dump(mess, s, sort_keys=True, indent=1)
                    hout=s.getvalue()
                    aaa="<h2>accounts info</h2><p><pre>%s</pre></p>" % (hout)			
                else:
                    mess = graph.put_wall_post(message, attachment=attachment)
                    #pprint.pprint(mess, s)
                    json.dump(mess, s, sort_keys=True, indent=1)
                    hout=s.getvalue()
                    aaa="<h2>wall post - ok </h2><p><a href=\"/fbputwall?cmd=delete&oid=%s\">delete</a></p><pre>%s</pre>" % (mess["id"],hout)			
        except Exception, e:
            errorjson = True
            errtext =  cgi.escape(str(sys.exc_info()[0])) + ' ' + cgi.escape(str(sys.exc_info()[1])) + ' ' + cgi.escape(str(sys.exc_info()[2]))
      else:
        aaa="<h2>wall post</h2>not loged - <a href=\"/auth/login?continue=%s\">login</a>" % (urllib.quote(req.request.uri))
    else:
      aaa="<h2>wall post</h2>not loged - <a href=\"/auth/login?continue=%s\">login</a>" % (urllib.quote(req.request.uri))
    bbb=""
    if errorjson:
        aaa=aaa+"%s" % (errtext)
    aaa="<h1>FaceBook User <a href=\"%s\">%s</a> info</h1><p>%s</p>" % (profile['link'],profile['id'],aaa)
    return aaa

class Friends(webapp.RequestHandler):
  def get(self):
    co2=20
    aaa=""
    pg=self.request.get('pg')
    if pg:
      pg = int(pg)
    else:
      pg=0

    args = dict(grant_type="client_credentials", client_id=FACEBOOK_APP_ID, client_secret=FACEBOOK_APP_SECRET)
    response = cgi.parse_qs(urllib.urlopen("https://graph.facebook.com/oauth/access_token?" +urllib.urlencode(args)).read())
#    response = cgi.parse_qs(urlfetch.fetch("https://graph.facebook.com/oauth/access_token?" +urllib.urlencode(args)).read())
    access_token = response["access_token"][-1]
    #print access_token
    graph = GraphAPI(access_token)
    #profile = graph.get_object(FACEBOOK_ID)
    #print profile
    #friends = graph.get_connections(FACEBOOK_ID, "friends")
    try:
	  friends = graph.request("/v2.3/me/friends")
    except Exception, e:
	  errorjson = True
	  errtext =  cgi.escape(str(sys.exc_info()[0])) + ' ' + cgi.escape(str(sys.exc_info()[1])) + ' ' + cgi.escape(str(sys.exc_info()[2]))
    if not errorjson:
#    friends = graph.get_connections(FACEBOOK_ID, "friends")
      co=len(friends["data"])
      i=0
      ii=0
      bbb=""
      while i<=co:
        i=i+co2
        if ii == pg:
          bbb=bbb+' '+str(ii)
        else:
          bbb=bbb+' '+"<a href=\"/fbf?pg="+ str(ii) +"\">"+ str(ii) +"</a>"
        ii=ii+1
      pg1=pg*co2
      pg2=pg1+co2
      if pg2>co:
        pg2=co
      if pg1>co:
        pg1=co
      i=pg1
      aaa=""
      while i<=pg2-1:
        friend=friends["data"][i]
#      print friend["name"],friend["id"]
        aaa=aaa+u"<a href=\"http://www.facebook.com/profile.php?id=%s\"><img src=\"http://graph.facebook.com/%s/picture\"/></a> <span style=\"font-size: 10pt\">   %s.   <strong>%s</strong>   <a href=\"/fbinfo?id=%s\">(Info)</a>  <a href=\"http://www.facebook.com/profile.php?id=%s\">(Profile)</a></span>" % (friend["id"],friend["id"], i+1, friend["name"],friend["id"],friend["id"])
        aaa=aaa+"<br>\n"
        i=i+1
      aaa=aaa+"<center>"+bbb+"</center><br>\n"
      aaa="<h1><a href=\"%s\">FaceBook</a> Friends (%s)</h1><p>%s</p>" % (FACEBOOK_URL,co,aaa)
    else:
      aaa="<h1><a href=\"%s\">FaceBook</a> Friends</h1><p>%s</p>" % (FACEBOOK_URL,errtext)
    self.response.out.write("<html><body> %s </body></html>" % (aaa))

app = webapp.WSGIApplication([('/fbf', Friends),('/fbinfo', FriendsInfo),('/fbputwall', FBPutWall),], debug=_DEBUG)


